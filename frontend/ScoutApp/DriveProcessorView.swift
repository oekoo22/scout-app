import SwiftUI

struct DriveProcessorView: View {
    @StateObject private var authService = AuthService() // Assumes AuthService.swift is accessible
    private let networkService = NetworkService() // Assumes NetworkService.swift is accessible

    @State private var googleDriveFileId: String = "" 
    @State private var taskPrompt: String = "Read this document, suggest a concise new name based on its content, find or create an appropriate folder for it, and then move it there."
    @State private var processingResult: String = ""
    @State private var isProcessing: Bool = false
    @State private var showAlert: Bool = false // Renamed from showErrorAlert for clarity
    @State private var alertMessage: String = ""

    var body: some View {
        // NavigationView allows for a title, though we might hide the main bar if it's within a TabView
        NavigationView {
            VStack(spacing: 15) {
                // Title can be part of the NavigationView or a Text element
                // Text("Google Drive Processor")
                //     .font(.title2)
                //     .padding(.top)

                if !authService.isAuthenticated {
                    Button("Authenticate with Google Drive") {
                        authService.authenticateWithGoogle { success, error in
                            if !success {
                                self.alertMessage = error?.localizedDescription ?? "Authentication failed. Ensure backend is running and callback URL scheme (e.g., scoutapp) is set in Info.plist."
                                self.showAlert = true
                            }
                        }
                    }
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                    .padding(.horizontal)
                } else {
                    Text("Authenticated with Google Drive!")
                        .foregroundColor(.green)
                        .padding(.vertical, 5)
                }

                TextField("Enter Google Drive File ID", text: $googleDriveFileId)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding(.horizontal)
                    .autocapitalization(.none)
                    .disableAutocorrection(true)

                TextEditor(text: $taskPrompt)
                    .frame(height: 100)
                    .border(Color.gray.opacity(0.5), width: 1)
                    .cornerRadius(5)
                    .padding(.horizontal)
                
                Button(action: processFile) {
                    Text(isProcessing ? "Processing..." : "Process File")
                }
                .padding()
                .frame(maxWidth: .infinity)
                .background(authService.isAuthenticated && !googleDriveFileId.isEmpty ? Color.green : Color.gray)
                .foregroundColor(.white)
                .cornerRadius(10)
                .padding(.horizontal)
                .disabled(!authService.isAuthenticated || googleDriveFileId.isEmpty || isProcessing)

                if isProcessing {
                    ProgressView()
                        .padding(.vertical, 5)
                }

                ScrollView {
                    Text(processingResult)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .lineLimit(nil) // Allow multiple lines
                }
                
                Spacer()
            }
            .navigationTitle("Google Drive") // Title for this tab's view
            .navigationBarTitleDisplayMode(.inline) // Or .large, depending on preference
            .alert(isPresented: $showAlert) {
                Alert(title: Text("Information"), message: Text(alertMessage), dismissButton: .default(Text("OK")))
            }
        }
    }

    func processFile() {
        guard authService.isAuthenticated else {
            self.alertMessage = "Please authenticate with Google Drive first."
            self.showAlert = true
            return
        }
        guard !googleDriveFileId.isEmpty else {
            self.alertMessage = "Please enter a Google Drive File ID."
            self.showAlert = true
            return
        }
        
        isProcessing = true
        processingResult = "Starting processing...\n"
        
        networkService.processDriveFile(fileId: googleDriveFileId, taskPrompt: taskPrompt) { result in
            isProcessing = false
            switch result {
            case .success(let response):
                var resultText = "🚀 Processing Successful!\n\n"
                resultText += "📄 Original File: \(response.original_file.name) (ID: \(response.original_file.id))\n"
                resultText += "✏️ Renamed File: \(response.renamed_file.name) (ID: \(response.renamed_file.id))\n"
                resultText += "📁 Target Folder: \(response.target_folder.name ?? "N/A") (ID: \(response.target_folder.id ?? "N/A"))\n"
                
                if let moveInfo = response.final_path_suggestion {
                     resultText += "➡️ Move Status: \(moveInfo.status ?? "Unknown")\n"
                     if let movedToId = moveInfo.moved_to_folder_id {
                         resultText += "    Moved to Folder ID: \(movedToId)\n"
                     }
                } else {
                    resultText += "➡️ Move Status: No move information available.\n"
                }
                
                resultText += "\n📋 Status Updates:\n"
                response.status_updates.forEach { update in
                    resultText += "- \(update)\n"
                }
                if let errorMsg = response.error_message, !errorMsg.isEmpty {
                    resultText += "\n⚠️ Backend Error: \(errorMsg)\n"
                }
                self.processingResult = resultText
                
            case .failure(let error):
                self.alertMessage = "Processing failed: \(error.localizedDescription)"
                self.showAlert = true
                self.processingResult = "❌ Error: \(error.localizedDescription)"
            }
        }
    }
}

struct DriveProcessorView_Previews: PreviewProvider {
    static var previews: some View {
        DriveProcessorView()
    }
}
