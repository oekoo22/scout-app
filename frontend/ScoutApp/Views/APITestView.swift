import SwiftUI

struct APITestView: View {
    @State private var helloWorldMessage: String = "Loading..."
    @State private var fileName: String = "test_file.pdf" // Default or placeholder
    @State private var orchestratorResponse: ScoutOrchestratorResponse? // Updated type
    @State private var errorMessage: String? // To display errors

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Hello World Section
                Text(helloWorldMessage)
                    .padding()
                    .onAppear {
                        fetchHelloWorld()
                    }
                
                Divider()
                
                // Orchestrator Section
                Text("Test Orchestrator")
                    .font(.headline)
                
                TextField("Enter PDF Filename (e.g., test_file.pdf)", text: $fileName)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding(.horizontal)
                
                Button("Process File via Orchestrator") {
                    triggerOrchestrator()
                }
                .padding()
                .buttonStyle(.borderedProminent)
                
                Button("Test Local PDF Processing") {
                    testLocalPDFProcessing()
                }
                .padding()
                .buttonStyle(.bordered)
                
                if let response = orchestratorResponse {
                    ScrollView {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Orchestrator Result:").font(.headline)
                            Text("Original File: \(response.original_file)")
                            
                            if let renamedFile = response.renamed_file {
                                Text("Renamed File: \(renamedFile)")
                            }
                            
                            if let targetFolder = response.target_folder {
                                Text("Target Folder: \(targetFolder)")
                            }
                            
                            if let finalPathSuggestion = response.final_path_suggestion {
                                Text("Final Path Suggestion: \(finalPathSuggestion)")
                            }
                            
                            Text("Status Updates:").font(.subheadline)
                            ForEach(response.status_updates, id: \.self) {
                                Text("- \($0)")
                            }
                            
                            if let errorMsg = response.error_message, !errorMsg.isEmpty {
                                Text("Error Message: \(errorMsg)").foregroundColor(.red)
                            }
                        }
                        .padding()
                    }
                }
                
                if let error = errorMessage {
                    Text("Error: \(error)")
                        .foregroundColor(.red)
                        .padding()
                }
                
                Spacer()
            }
            .navigationTitle("API Tester")
        }
    }
    
    func fetchHelloWorld() {
        APIService.shared.fetchHelloWorld { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let response):
                    helloWorldMessage = response
                case .failure(let error):
                    helloWorldMessage = "Error: \(error.localizedDescription)"
                }
            }
        }
    }
    
    func triggerOrchestrator() {
        orchestratorResponse = nil // Clear previous results
        errorMessage = nil       // Clear previous errors
        
        guard !fileName.isEmpty else {
            errorMessage = "File name cannot be empty."
            return
        }
        
        APIService.shared.triggerOrchestrator(fileName: fileName) { result in // Updated function call
            DispatchQueue.main.async {
                switch result {
                case .success(let response):
                    self.orchestratorResponse = response
                    if let backendError = response.error_message {
                        self.errorMessage = "Backend processing error: \(backendError)"
                    }
                case .failure(let error):
                    self.orchestratorResponse = nil // Clear response on failure
                    self.errorMessage = "API Call Failed: \(error.localizedDescription)"
                    // For more detailed error, you might want to switch on APIError cases
                    switch error {
                    case .decodingFailed(let decodingError):
                        self.errorMessage = "Failed to decode response: \(decodingError.localizedDescription)"
                    case .encodingFailed(let encodingError):
                        self.errorMessage = "Failed to encode request: \(encodingError.localizedDescription)"
                    case .invalidURL:
                        self.errorMessage = "Invalid API URL."
                    case .requestFailed(let reqError):
                        self.errorMessage = "Network request failed: \(reqError.localizedDescription)"
                    case .invalidResponse:
                        self.errorMessage = "Invalid response from server (e.g., non-200 or unparseable error)."
                    }
                }
            }
        }
    }
    
    func testLocalPDFProcessing() {
        orchestratorResponse = nil // Clear previous results
        errorMessage = nil       // Clear previous errors
        
        // Load the actual test_file.pdf from the app bundle
        guard let pdfData = loadTestPDFFromBundle() else {
            errorMessage = "Failed to load test_file.pdf from app bundle. Make sure the file is included in the project."
            return
        }
        
        let testFileName = "test_file.pdf"
        
        APIService.shared.processLocalPDF(pdfData: pdfData, fileName: testFileName) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let response):
                    self.orchestratorResponse = response
                    if let backendError = response.error_message {
                        self.errorMessage = "Backend processing error: \(backendError)"
                    }
                case .failure(let error):
                    self.orchestratorResponse = nil // Clear response on failure
                    self.errorMessage = "Local PDF Test Failed: \(error.localizedDescription)"
                    switch error {
                    case .decodingFailed(let decodingError):
                        self.errorMessage = "Failed to decode response: \(decodingError.localizedDescription)"
                    case .encodingFailed(let encodingError):
                        self.errorMessage = "Failed to encode request: \(encodingError.localizedDescription)"
                    case .invalidURL:
                        self.errorMessage = "Invalid API URL."
                    case .requestFailed(let reqError):
                        self.errorMessage = "Network request failed: \(reqError.localizedDescription)"
                    case .invalidResponse:
                        self.errorMessage = "Invalid response from server (e.g., non-200 or unparseable error)."
                    }
                }
            }
        }
    }
    
    func loadTestPDFFromBundle() -> Data? {
        // Load the actual test_file.pdf from the app bundle
        guard let url = Bundle.main.url(forResource: "test_file", withExtension: "pdf") else {
            print("Error: test_file.pdf not found in app bundle")
            return nil
        }
        
        do {
            let data = try Data(contentsOf: url)
            print("Successfully loaded test_file.pdf from bundle (\(data.count) bytes)")
            return data
        } catch {
            print("Error loading test_file.pdf: \(error.localizedDescription)")
            return nil
        }
    }
}

struct APITestView_Previews: PreviewProvider {
    static var previews: some View {
        APITestView()
    }
}
