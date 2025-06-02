import Foundation

// Request body for /process-file
struct ProcessFileRequest: Codable {
    let file_name: String // This will be the Google Drive File ID
    let task_prompt: String
}

// Response structure from /process-file
struct ProcessFileResponse: Codable {
    struct FileInfo: Codable {
        let id: String
        let name: String
        
        // Custom initializer for when we have a simple string instead of a structured object
        init(from decoder: Decoder) throws {
            // First try to decode as a string
            do {
                let container = try decoder.singleValueContainer()
                if let stringValue = try? container.decode(String.self) {
                    // If it's a string, use it as both id and name
                    self.id = stringValue
                    self.name = stringValue
                    return
                }
            } catch {}
            
            // Fall back to normal decoding if not a string
            let container = try decoder.container(keyedBy: CodingKeys.self)
            id = try container.decode(String.self, forKey: .id)
            name = try container.decode(String.self, forKey: .name)
        }
        
        enum CodingKeys: String, CodingKey {
            case id, name
        }
    }
    
    struct FolderInfo: Codable {
        let name: String?
        let id: String?
        
        // Custom initializer for when we have a simple string instead of a structured object
        init(from decoder: Decoder) throws {
            // First try to decode as a string
            do {
                let container = try decoder.singleValueContainer()
                if let stringValue = try? container.decode(String.self) {
                    // If it's a string, use it as both id and name
                    self.id = stringValue
                    self.name = stringValue
                    return
                }
            } catch {}
            
            // Fall back to normal decoding if not a string
            let container = try decoder.container(keyedBy: CodingKeys.self)
            id = try container.decodeIfPresent(String.self, forKey: .id)
            name = try container.decodeIfPresent(String.self, forKey: .name)
        }
        
        enum CodingKeys: String, CodingKey {
            case id, name
        }
    }
    
    // Matching the orchestrator's 'final_moved_path_info' which is FileMoveConfirmation model
    struct MovedPathInfo: Codable { 
        let file_id: String?
        let moved_to_folder_id: String?
        let status: String?
        // Add other fields if your FileMoveConfirmation model has more, e.g., new_file_name
        
        // Custom initializer for when we have a simple string instead of a structured object
        init(from decoder: Decoder) throws {
            // First try to decode as a string
            do {
                let container = try decoder.singleValueContainer()
                if let stringValue = try? container.decode(String.self) {
                    // If it's a string, use it as status and leave other fields nil
                    self.status = stringValue
                    self.file_id = nil
                    self.moved_to_folder_id = nil
                    return
                }
            } catch {}
            
            // Fall back to normal decoding if not a string
            let container = try decoder.container(keyedBy: CodingKeys.self)
            file_id = try container.decodeIfPresent(String.self, forKey: .file_id)
            moved_to_folder_id = try container.decodeIfPresent(String.self, forKey: .moved_to_folder_id)
            status = try container.decodeIfPresent(String.self, forKey: .status)
        }
        
        enum CodingKeys: String, CodingKey {
            case file_id, moved_to_folder_id, status
        }
    }

    let original_file: FileInfo
    let renamed_file: FileInfo
    let target_folder: FolderInfo
    let final_path_suggestion: MovedPathInfo? // Key from orchestrator output
    let status_updates: [String]
    let error_message: String?
}

class NetworkService {
    // Ensure this URL points to your running backend
    private let backendURL = URL(string: "http://localhost:8000")!

    func processDriveFile(fileId: String, taskPrompt: String, completion: @escaping (Result<ProcessFileResponse, Error>) -> Void) {
        let url = backendURL.appendingPathComponent("/process-file")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        let requestBody = ProcessFileRequest(file_name: fileId, task_prompt: taskPrompt)
        do {
            request.httpBody = try JSONEncoder().encode(requestBody)
        } catch {
            completion(.failure(error))
            return
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
                return
            }

            guard let httpResponse = response as? HTTPURLResponse else {
                DispatchQueue.main.async {
                    completion(.failure(NSError(domain: "NetworkService", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid HTTP response"])))
                }
                return
            }
            
            print("Process File Response Status Code: \(httpResponse.statusCode)")
            if let rawData = data, let rawString = String(data: rawData, encoding: .utf8) {
                 print("Raw Response Data: \(rawString)")
            }

            if (200...299).contains(httpResponse.statusCode) {
                guard let data = data else {
                    DispatchQueue.main.async {
                        completion(.failure(NSError(domain: "NetworkService", code: 0, userInfo: [NSLocalizedDescriptionKey: "No data received"])))
                    }
                    return
                }
                do {
                    let decodedResponse = try JSONDecoder().decode(ProcessFileResponse.self, from: data)
                    DispatchQueue.main.async {
                        completion(.success(decodedResponse))
                    }
                } catch {
                    print("Decoding error: \(error)")
                    DispatchQueue.main.async {
                        completion(.failure(error))
                    }
                }
            } else {
                var errorMessage = "Server error: \(httpResponse.statusCode)"
                if let data = data, 
                   let errorResponse = try? JSONDecoder().decode([String: String].self, from: data), 
                   let detail = errorResponse["detail"] {
                    errorMessage = detail
                } else if let data = data, let rawString = String(data: data, encoding: .utf8), !rawString.isEmpty {
                    errorMessage += " - \(rawString)"
                } else if httpResponse.statusCode == 401 {
                    errorMessage = "Authentication failed or token expired. Please authenticate again."
                }
                DispatchQueue.main.async {
                    completion(.failure(NSError(domain: "NetworkService", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
                }
            }
        }.resume()
    }
}
