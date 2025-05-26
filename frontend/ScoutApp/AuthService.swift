import SwiftUI
import AuthenticationServices

class AuthService: NSObject, ObservableObject {
    @Published var isAuthenticated: Bool = false
    private var accessToken: String? // Store the token
    private var authSession: ASWebAuthenticationSession?

    // Ensure this URL points to your running backend
    private let backendURL = "http://localhost:8000" // Ensure this is correct
    let callbackURLScheme = "scoutapp" // Must match Info.plist
    private let userDefaultsTokenKey = "googleDriveAccessToken"

    override init() {
        super.init()
        // Try to load token on init
        if let savedToken = UserDefaults.standard.string(forKey: userDefaultsTokenKey) {
            self.accessToken = savedToken
            self.isAuthenticated = true
            print("AuthService: Loaded token from UserDefaults. User is authenticated.")
        } else {
            print("AuthService: No token found in UserDefaults.")
        }
    }

    func authenticateWithGoogle(completion: @escaping (Bool, Error?) -> Void) {
        guard let authURL = URL(string: "\(backendURL)/auth/google?callback_scheme=\(callbackURLScheme)") else {
            print("Error: Invalid authentication URL")
            completion(false, NSError(domain: "AuthService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid authentication URL."]))
            return
        }

        self.authSession = ASWebAuthenticationSession(url: authURL, callbackURLScheme: callbackURLScheme) { callbackURL, error in
            DispatchQueue.main.async {
                if let error = error {
                    print("Authentication error: \(error.localizedDescription)")
                    // Handle specific errors like user cancellation
                    if let authError = error as? ASWebAuthenticationSessionError, authError.code == .canceledLogin {
                        print("User cancelled authentication.")
                        completion(false, authError)
                    } else {
                        completion(false, error)
                    }
                    return
                }

                guard let callbackURL = callbackURL else {
                    print("Error: Callback URL is nil")
                    completion(false, NSError(domain: "AuthService", code: -2, userInfo: [NSLocalizedDescriptionKey: "Callback URL is nil."]))
                    return
                }

                print("Callback URL received: \(callbackURL.absoluteString)")

                // Extract token from callback URL (e.g., scoutapp://?token=YOUR_TOKEN)
                let components = URLComponents(url: callbackURL, resolvingAgainstBaseURL: false)
                if let tokenItem = components?.queryItems?.first(where: { $0.name == "token" }) {
                    self.accessToken = tokenItem.value
                    self.isAuthenticated = true
                    UserDefaults.standard.set(self.accessToken, forKey: self.userDefaultsTokenKey) // Save token
                    print("Authentication successful. Token: \(self.accessToken ?? "N/A")")
                    completion(true, nil)
                } else {
                    print("Error: Token not found in callback URL. Query items: \(components?.queryItems ?? [])")
                    self.isAuthenticated = false
                    completion(false, NSError(domain: "AuthService", code: -3, userInfo: [NSLocalizedDescriptionKey: "Token not found in callback URL."]))
                }
            }
        }

        self.authSession?.presentationContextProvider = self
        self.authSession?.prefersEphemeralWebBrowserSession = false // Set to false for testing
        self.authSession?.start()
    }
    
    func signOut() {
        DispatchQueue.main.async {
            self.accessToken = nil
            self.isAuthenticated = false
            UserDefaults.standard.removeObject(forKey: self.userDefaultsTokenKey) // Clear token
            print("User signed out.")
        }
    }
}

extension AuthService: ASWebAuthenticationPresentationContextProviding {
    func presentationAnchor(for session: ASWebAuthenticationSession) -> ASPresentationAnchor {
        return UIApplication.shared.windows.first { $0.isKeyWindow } ?? ASPresentationAnchor()
    }
}
