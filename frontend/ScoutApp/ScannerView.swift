import SwiftUI
import AVFoundation
import VisionKit
import PDFKit

struct ScannerView: View {
    @StateObject private var camera = CameraController()
    @State private var showingDocumentScanner = false
    @State private var scannedDocuments: [UIImage] = []
    
    var body: some View {
        ZStack {
            if !showingDocumentScanner {
                CameraPreview(camera: camera)
                    .ignoresSafeArea()
                
                VStack {
                    Spacer()
                    HStack(spacing: 50) {
                        Button(action: {
                            showingDocumentScanner = true
                        }) {
                            VStack {
                                Image(systemName: "doc.viewfinder")
                                    .resizable()
                                    .frame(width: 50, height: 50)
                                    .foregroundColor(.white)
                                Text("Document Scanner")
                                    .foregroundColor(.white)
                                    .font(.caption)
                            }
                        }
                        
                        Button(action: {
                            camera.captureImage()
                        }) {
                            VStack {
                                Image(systemName: "camera.circle.fill")
                                    .resizable()
                                    .frame(width: 70, height: 70)
                                    .foregroundColor(.white)
                                Text("Photo")
                                    .foregroundColor(.white)
                                    .font(.caption)
                            }
                        }
                    }
                    .padding(.bottom, 30)
                }
            }
        }
        .onAppear {
            camera.checkPermissions()
        }
        .sheet(isPresented: $camera.showImagePreview) {
            if let image = camera.capturedImage {
                ImagePreviewView(image: image, onSave: { processedImage in
                    Task {
                        await createAndUploadPDF(from: [processedImage])
                    }
                }, isPresented: $camera.showImagePreview)
            }
        }
        .sheet(isPresented: $showingDocumentScanner) {
            DocumentScannerView { images in
                scannedDocuments = images
                Task {
                    await createAndUploadPDF(from: images)
                }
            }
        }
    }
    
    private func createAndUploadPDF(from images: [UIImage]) async {
        guard !images.isEmpty else { return }
        
        let pdfDocument = PDFDocument()
        
        for (index, image) in images.enumerated() {
            if let pdfPage = PDFPage(image: image) {
                pdfDocument.insert(pdfPage, at: index)
            }
        }
        
        let fileName = "ScannedDocument_\(Date().timeIntervalSince1970).pdf"
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let pdfPath = documentsPath.appendingPathComponent(fileName)
        
        pdfDocument.write(to: pdfPath)
        
        // Upload to Google Drive via backend
        guard let pdfData = pdfDocument.dataRepresentation() else {
            print("Failed to generate PDF data")
            return
        }
        
        await MainActor.run {
            APIService.shared.processLocalPDF(pdfData: pdfData, fileName: fileName) { result in
                DispatchQueue.main.async {
                    switch result {
                    case .success(let response):
                        print("PDF processed locally: \(response)")
                        // Show success message to user
                    case .failure(let error):
                        print("Failed to process PDF: \(error)")
                        // Show error message to user
                    }
                }
            }
        }
    }
}

class CameraController: NSObject, ObservableObject {
    private var session: AVCaptureSession?
    private var photoOutput = AVCapturePhotoOutput()
    private var previewLayer: AVCaptureVideoPreviewLayer?
    
    @Published var capturedImage: UIImage?
    @Published var showImagePreview = false
    
    func checkPermissions() {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            setupCamera()
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { granted in
                if granted {
                    DispatchQueue.main.async {
                        self.setupCamera()
                    }
                }
            }
        default:
            break
        }
    }
    
    private func setupCamera() {
        let session = AVCaptureSession()
        session.sessionPreset = .photo
        
        guard let device = AVCaptureDevice.default(for: .video),
              let input = try? AVCaptureDeviceInput(device: device) else { return }
        
        session.beginConfiguration()
        
        if session.canAddInput(input) {
            session.addInput(input)
        }
        
        if session.canAddOutput(photoOutput) {
            session.addOutput(photoOutput)
        }
        
        session.commitConfiguration()
        
        let previewLayer = AVCaptureVideoPreviewLayer(session: session)
        previewLayer.videoGravity = .resizeAspectFill
        self.previewLayer = previewLayer
        
        DispatchQueue.global(qos: .background).async {
            session.startRunning()
        }
        
        self.session = session
    }
    
    func captureImage() {
        let settings = AVCapturePhotoSettings()
        photoOutput.capturePhoto(with: settings, delegate: self)
    }
    
    func getPreviewLayer() -> AVCaptureVideoPreviewLayer? {
        return previewLayer
    }
}

extension CameraController: AVCapturePhotoCaptureDelegate {
    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        guard let imageData = photo.fileDataRepresentation(),
              let image = UIImage(data: imageData) else { return }
        
        DispatchQueue.main.async {
            self.capturedImage = image
            self.showImagePreview = true
        }
    }
}

struct CameraPreview: UIViewRepresentable {
    let camera: CameraController
    
    func makeUIView(context: Context) -> UIView {
        let view = UIView(frame: UIScreen.main.bounds)
        view.backgroundColor = .black
        
        if let previewLayer = camera.getPreviewLayer() {
            previewLayer.frame = view.bounds
            view.layer.addSublayer(previewLayer)
        }
        
        return view
    }
    
    func updateUIView(_ uiView: UIView, context: Context) {
        if let previewLayer = camera.getPreviewLayer() {
            previewLayer.frame = uiView.bounds
        }
    }
}

struct DocumentScannerView: UIViewControllerRepresentable {
    let completion: ([UIImage]) -> Void
    
    func makeUIViewController(context: Context) -> VNDocumentCameraViewController {
        let scanner = VNDocumentCameraViewController()
        scanner.delegate = context.coordinator
        return scanner
    }
    
    func updateUIViewController(_ uiViewController: VNDocumentCameraViewController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(completion: completion)
    }
    
    class Coordinator: NSObject, VNDocumentCameraViewControllerDelegate {
        let completion: ([UIImage]) -> Void
        
        init(completion: @escaping ([UIImage]) -> Void) {
            self.completion = completion
        }
        
        func documentCameraViewController(_ controller: VNDocumentCameraViewController, didFinishWith scan: VNDocumentCameraScan) {
            var images: [UIImage] = []
            for pageIndex in 0..<scan.pageCount {
                images.append(scan.imageOfPage(at: pageIndex))
            }
            completion(images)
            controller.dismiss(animated: true)
        }
        
        func documentCameraViewControllerDidCancel(_ controller: VNDocumentCameraViewController) {
            controller.dismiss(animated: true)
        }
        
        func documentCameraViewController(_ controller: VNDocumentCameraViewController, didFailWithError error: Error) {
            controller.dismiss(animated: true)
        }
    }
}

struct ImagePreviewView: View {
    let image: UIImage
    let onSave: (UIImage) -> Void
    @Binding var isPresented: Bool
    
    var body: some View {
        NavigationView {
            VStack {
                Image(uiImage: image)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .padding()
                
                Spacer()
                
                HStack(spacing: 30) {
                    Button("Cancel") {
                        isPresented = false
                    }
                    .foregroundColor(.red)
                    
                    Button("Save as PDF") {
                        onSave(image)
                        isPresented = false
                    }
                    .foregroundColor(.blue)
                    .fontWeight(.bold)
                }
                .padding()
            }
            .navigationTitle("Preview")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

#Preview {
    ScannerView()
}
