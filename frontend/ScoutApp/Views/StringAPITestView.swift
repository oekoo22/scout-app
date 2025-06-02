import SwiftUI

struct StringAPITestView: View {
    @State private var fileName: String = "1Q96ibz1ahHCr52NR85fIsoZMuw1f6KLQ8rmW7hlYMqc" // Default Google Drive File ID
    @State private var response: StringOrchestratorResponse?
    @State private var errorMessage: String?
    @State private var isProcessing: Bool = false
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Google Drive File Test")
                .font(.headline)
            
            TextField("Enter Google Drive File ID", text: $fileName)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
            
            Button(action: {
                processFile()
            }) {
                Text(isProcessing ? "Processing..." : "Process File")
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(isProcessing ? Color.gray : Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
            .disabled(isProcessing || fileName.isEmpty)
            .padding(.horizontal)
            
            if isProcessing {
                ProgressView()
            }
            
            if let error = errorMessage {
                Text("Error: \(error)")
                    .foregroundColor(.red)
                    .padding()
                    .multilineTextAlignment(.leading)
            }
            
            if let response = response {
                ScrollView {
                    VStack(alignment: .leading, spacing: 10) {
                        Group {
                            Text("Original File ID: \(response.original_file)")
                                .fontWeight(.bold)
                            
                            if let renamed = response.renamed_file {
                                Text("Renamed File: \(renamed)")
                            }
                            
                            if let folder = response.target_folder {
                                Text("Target Folder: \(folder)")
                            }
                            
                            if let path = response.final_path_suggestion {
                                Text("Final Path: \(path)")
                            }
                        }
                        .padding(.vertical, 2)
                        
                        Divider()
                        
                        Text("Status Updates:")
                            .fontWeight(.bold)
                        
                        ForEach(Array(response.status_updates.enumerated()), id: \.offset) { index, update in
                            Text("• \(update)")
                                .font(.footnote)
                                .padding(.vertical, 1)
                        }
                        
                        if let error = response.error_message {
                            Divider()
                            Text("Backend Error: \(error)")
                                .foregroundColor(.red)
                                .fontWeight(.bold)
                        }
                    }
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
            
            Spacer()
        }
        .padding()
        .navigationTitle("String API Test")
    }
    
    func processFile() {
        guard !fileName.isEmpty else {
            errorMessage = "Please enter a file ID"
            return
        }
        
        isProcessing = true
        errorMessage = nil
        response = nil
        
        StringAPIService.shared.triggerOrchestrator(fileName: fileName) { result in
            DispatchQueue.main.async {
                isProcessing = false
                
                switch result {
                case .success(let response):
                    self.response = response
                    self.errorMessage = nil
                    
                case .failure(let error):
                    self.errorMessage = "Failed to process file: \(error.localizedDescription)"
                    self.response = nil
                }
            }
        }
    }
}

struct StringAPITestView_Previews: PreviewProvider {
    static var previews: some View {
        StringAPITestView()
    }
}
