import Foundation

struct AppConfig {
    
    // MARK: - Environment Detection
    static var environment: Environment {
        #if DEBUG
        return .development
        #else
        return .production
        #endif
    }
    
    // MARK: - Backend Configuration
    static var backendBaseURL: String {
        // Check for a manually set backend URL first (for testing)
        if let manualURL = UserDefaults.standard.string(forKey: "manual_backend_url"), !manualURL.isEmpty {
            return manualURL
        }
        
        // Default configuration based on environment
        switch environment {
        case .development:
            return "http://localhost:8000"
        case .production:
            return "https://your-production-domain.com" // Update this for production
        }
    }
    
    // MARK: - OAuth Configuration
    static let callbackURLScheme = "scoutapp"
    
    // MARK: - Network Configuration
    static let defaultTimeout: TimeInterval = 30.0
    
    // MARK: - User Defaults Keys
    struct UserDefaultsKeys {
        static let googleDriveAccessToken = "googleDriveAccessToken"
        static let manualBackendURL = "manual_backend_url"
        static let lastBackendHealth = "last_backend_health"
    }
    
    // MARK: - Helper Methods
    
    /// Get the auth URL for Google OAuth
    static func getAuthURL() -> URL? {
        return URL(string: "\(backendBaseURL)/auth/google?callback_scheme=\(callbackURLScheme)")
    }
    
    /// Get the health check URL
    static func getHealthURL() -> URL? {
        return URL(string: "\(backendBaseURL)/health")
    }
    
    /// Get the config URL
    static func getConfigURL() -> URL? {
        return URL(string: "\(backendBaseURL)/config")
    }
    
    /// Set a manual backend URL (useful for testing with local IP)
    static func setManualBackendURL(_ url: String) {
        UserDefaults.standard.set(url, forKey: UserDefaultsKeys.manualBackendURL)
        print("AppConfig: Manual backend URL set to: \(url)")
    }
    
    /// Clear manual backend URL
    static func clearManualBackendURL() {
        UserDefaults.standard.removeObject(forKey: UserDefaultsKeys.manualBackendURL)
        print("AppConfig: Manual backend URL cleared")
    }
    
    /// Get current configuration info
    static func getInfo() -> [String: String] {
        return [
            "environment": environment.rawValue,
            "backendBaseURL": backendBaseURL,
            "callbackURLScheme": callbackURLScheme,
            "hasManualURL": UserDefaults.standard.string(forKey: UserDefaultsKeys.manualBackendURL) != nil ? "Yes" : "No"
        ]
    }
}

// MARK: - Environment Enum
enum Environment: String {
    case development = "development"
    case production = "production"
}