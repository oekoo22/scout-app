import Foundation

enum APIError: Error {
    case invalidURL
    case requestFailed(Error)
    case invalidResponse
    case decodingFailed(Error)
    case encodingFailed(Error)
}

struct ScoutOrchestratorResponse: Codable, Identifiable {
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

class APIService {
    static let shared = APIService()
    
    private let baseURL = "http://localhost:8000"
    
    private init() {}
    
    func fetchHelloWorld(completion: @escaping (Result<String, APIError>) -> Void) {
        guard let url = URL(string: "\(baseURL)/") else {
            completion(.failure(.invalidURL))
            return
        }
        
        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(.requestFailed(error)))
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                completion(.failure(.invalidResponse))
                return
            }
            
            if let data = data {
                do {
                    let result = try JSONDecoder().decode([String: String].self, from: data)
                    if let message = result["message"] {
                        completion(.success(message))
                    } else {
                        completion(.failure(.decodingFailed(NSError(domain: "", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid response format"]))))
                    }
                } catch {
                    completion(.failure(.decodingFailed(error)))
                }
            }
        }
        
        task.resume()
    }
    
    func triggerOrchestrator(fileName: String, completion: @escaping (Result<ScoutOrchestratorResponse, APIError>) -> Void) {
        guard let url = URL(string: "\(baseURL)/process-file") else {
            completion(.failure(.invalidURL))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["file_name": fileName]
        do {
            request.httpBody = try JSONEncoder().encode(body)
        } catch {
            completion(.failure(.encodingFailed(error)))
            return
        }
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(.requestFailed(error)))
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse else {
                completion(.failure(.invalidResponse))
                return
            }
            
            guard (200...299).contains(httpResponse.statusCode), let data = data else {
                let errorMessage = "Server returned status \(httpResponse.statusCode)"
                completion(.failure(.requestFailed(NSError(domain: "APIService.HTTPError", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: errorMessage]))))
                return
            }
            
            // For debugging - print raw JSON
            if let jsonString = String(data: data, encoding: .utf8) {
                print("APIService: Response JSON: \(jsonString)")
            }
            
            do {
                let result = try JSONDecoder().decode(ScoutOrchestratorResponse.self, from: data)
                completion(.success(result))
            } catch {
                print("APIService: Decoding error: \(error)")
                if let decodingError = error as? DecodingError {
                    self.printDetailedDecodingError(decodingError)
                }
                completion(.failure(.decodingFailed(error)))
            }
        }
        
        task.resume()
    }
    
    // Add more API calls here as needed

    // Helper function to print detailed decoding errors (add this inside APIService class)
    private func printDetailedDecodingError(_ error: DecodingError) {
        print("APIService: Decoding Error Details:")
        switch error {
        case .typeMismatch(let type, let context):
            print("  Type Mismatch: '\(type)'")
            print("  CodingPath: \(context.codingPath.map { $0.stringValue }.joined(separator: "."))")
            print("  Debug Description: \(context.debugDescription)")
            if let underlying = context.underlyingError {
                 print("  Underlying error: \(underlying)")
            }
        case .valueNotFound(let type, let context):
            print("  Value Not Found: '\(type)'")
            print("  CodingPath: \(context.codingPath.map { $0.stringValue }.joined(separator: "."))")
            print("  Debug Description: \(context.debugDescription)")
        case .keyNotFound(let key, let context):
            print("  Key Not Found: '\(key.stringValue)'")
            print("  CodingPath: \(context.codingPath.map { $0.stringValue }.joined(separator: "."))")
            print("  Debug Description: \(context.debugDescription)")
        case .dataCorrupted(let context):
            print("  Data Corrupted:")
            print("  CodingPath: \(context.codingPath.map { $0.stringValue }.joined(separator: "."))")
            print("  Debug Description: \(context.debugDescription)")
        @unknown default:
            print("  Unknown decoding error.")
        }
    }
}
