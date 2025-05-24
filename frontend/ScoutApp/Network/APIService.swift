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
            
            guard (200...299).contains(httpResponse.statusCode) else {
                if let data = data {
                    do {
                        let errorResponse = try JSONDecoder().decode(ScoutOrchestratorResponse.self, from: data)
                        print("Backend error response: \(errorResponse)")
                        completion(.failure(.invalidResponse))
                    } catch {
                        completion(.failure(.invalidResponse))
                    }
                } else {
                    completion(.failure(.invalidResponse))
                }
                return
            }
            
            guard let data = data else {
                completion(.failure(.invalidResponse))
                return
            }
            
            do {
                let result = try JSONDecoder().decode(ScoutOrchestratorResponse.self, from: data)
                completion(.success(result))
            } catch {
                completion(.failure(.decodingFailed(error)))
            }
        }
        
        task.resume()
    }
    
    // Add more API calls here as needed
}
