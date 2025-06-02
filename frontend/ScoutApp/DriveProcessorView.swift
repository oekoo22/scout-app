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

    // Computed property for button state with logging
    private var isProcessButtonEnabled: Bool {
        let enabled = authService.isAuthenticated && !googleDriveFileId.isEmpty && !isProcessing
        // This print will go to your Xcode console
        print("isProcessButtonEnabled: \(enabled) | isAuthenticated: \(authService.isAuthenticated), fileIdIsEmpty: \(googleDriveFileId.isEmpty), isProcessing: \(isProcessing)")
        return enabled
    }

    var body: some View {
        // Optional: To see when the body itself re-evaluates, you can add a print here too
        // let _ = print("DriveProcessorView body re-evaluating")
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
                    VStack {
                        Text("Authenticated with Google Drive!")
                            .foregroundColor(.green)
                            .padding(.vertical, 5)
                        Button("Sign Out") {
                            authService.signOut()
                        }
                        .padding(5)
                        .foregroundColor(.red)
                    }
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
                .background(isProcessButtonEnabled ? Color.green : Color.gray) // Use computed property for background too
                .foregroundColor(.white)
                .cornerRadius(10)
                .padding(.horizontal)
                .disabled(!isProcessButtonEnabled) // Use computed property here

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
                
                // Handle original file display - either as plain string or with ID if different
                if response.original_file.name == response.original_file.id {
                    resultText += "📄 Original File: \(response.original_file.name)\n"
                } else {
                    resultText += "📄 Original File: \(response.original_file.name) (ID: \(response.original_file.id))\n"
                }
                
                // Handle renamed file display
                if response.renamed_file.name == response.renamed_file.id {
                    resultText += "✏️ Renamed File: \(response.renamed_file.name)\n"
                } else {
                    resultText += "✏️ Renamed File: \(response.renamed_file.name) (ID: \(response.renamed_file.id))\n"
                }
                
                // Handle target folder display
                let folderName = response.target_folder.name ?? "N/A"
                let folderId = response.target_folder.id ?? "N/A"
                if folderId == folderName {
                    resultText += "📁 Target Folder: \(folderName)\n"
                } else {
                    resultText += "📁 Target Folder: \(folderName) (ID: \(folderId))\n"
                }
                
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
