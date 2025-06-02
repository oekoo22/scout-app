import Foundation

// Simple string-based response model for handling the orchestrator output
struct StringOrchestratorResponse: Codable, Identifiable {
    var id = UUID()
    let original_file: String
    let renamed_file: String?
    let target_folder: String?
    let final_path_suggestion: String?
    let status_updates: [String]
    let error_message: String?
    
    private enum CodingKeys: String, CodingKey {
        case original_file, renamed_file, target_folder, final_path_suggestion, status_updates, error_message
    }
}

class StringAPIService {
    static let shared = StringAPIService()
    private let baseURL = "http://localhost:8000"
    
    private init() {}
    
    func fetchHelloWorld(completion: @escaping (Result<String, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/") else {
            completion(.failure(NSError(domain: "StringAPIService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"])))
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                completion(.failure(NSError(domain: "StringAPIService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid response"])))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "StringAPIService", code: -1, userInfo: [NSLocalizedDescriptionKey: "No data received"])))
                return
            }
            
            do {
                let result = try JSONDecoder().decode([String: String].self, from: data)
                if let message = result["message"] {
                    completion(.success(message))
                } else {
                    completion(.failure(NSError(domain: "StringAPIService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid response format"])))
                }
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    func triggerOrchestrator(fileName: String, completion: @escaping (Result<StringOrchestratorResponse, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/process-file") else {
            completion(.failure(NSError(domain: "StringAPIService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"])))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["file_name": fileName]
        
        do {
            request.httpBody = try JSONEncoder().encode(body)
        } catch {
            completion(.failure(error))
            return
        }
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse else {
                completion(.failure(NSError(domain: "StringAPIService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid HTTP response"])))
                return
            }
            
            print("StringAPIService - Status Code: \(httpResponse.statusCode)")
            
            guard (200...299).contains(httpResponse.statusCode), let data = data else {
                let message = "Server returned status \(httpResponse.statusCode)"
                completion(.failure(NSError(domain: "StringAPIService", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: message])))
                return
            }
            
            // Print raw JSON for debugging
            if let jsonString = String(data: data, encoding: .utf8) {
                print("StringAPIService - Raw Response: \(jsonString)")
            }
            
            do {
                // Create a decoder with explicit string decoding strategy
                let decoder = JSONDecoder()
                let response = try decoder.decode(StringOrchestratorResponse.self, from: data)
                completion(.success(response))
            } catch {
                print("StringAPIService - Decoding Error: \(error)")
                
                // Detailed error analysis
                if let decodingError = error as? DecodingError {
                    switch decodingError {
                    case .keyNotFound(let key, let context):
                        print("  Key '\(key.stringValue)' not found: \(context.debugDescription)")
                    case .typeMismatch(let type, let context):
                        print("  Type '\(type)' mismatch: \(context.debugDescription)")
                        print("  JSON path: \(context.codingPath.map { $0.stringValue }.joined(separator: "."))")
                    case .valueNotFound(let type, let context):
                        print("  Value of type '\(type)' not found: \(context.debugDescription)")
                    case .dataCorrupted(let context):
                        print("  Data corrupted: \(context.debugDescription)")
                    @unknown default:
                        print("  Unknown decoding error")
                    }
                }
                
                completion(.failure(error))
            }
        }.resume()
    }
}
