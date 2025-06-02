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

                // Temporarily check for status=success instead of token
                let components = URLComponents(url: callbackURL, resolvingAgainstBaseURL: false)
                if let statusItem = components?.queryItems?.first(where: { $0.name == "status" }), statusItem.value == "success" {
                    self.isAuthenticated = true // Mark as authenticated for testing purposes
                    self.accessToken = "dummy_success_token" // Set a dummy token or handle appropriately
                    UserDefaults.standard.set(self.accessToken, forKey: self.userDefaultsTokenKey) // Save dummy token
                    print("Authentication successful (status=success received).")
                    completion(true, nil)
                } else {
                    print("Error: 'status=success' not found in callback URL. Query items: \(components?.queryItems ?? [])")
                    self.isAuthenticated = false
                    completion(false, NSError(domain: "AuthService", code: -3, userInfo: [NSLocalizedDescriptionKey: "'status=success' not found in callback URL."]))
                }
            }
        }

        self.authSession?.presentationContextProvider = self
        self.authSession?.prefersEphemeralWebBrowserSession = true // Recommended for auth testing
        if let sessionStarted = self.authSession?.start(), sessionStarted {
            print("ASWebAuthenticationSession started successfully.")
        } else {
            print("ASWebAuthenticationSession FAILED to start.")
            completion(false, NSError(domain: "AuthService", code: -4, userInfo: [NSLocalizedDescriptionKey: "ASWebAuthenticationSession failed to start."]))
            return
        }
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
        if #available(iOS 15, *) {
            let scenes = UIApplication.shared.connectedScenes
            let windowScene = scenes.first(where: { $0.activationState == .foregroundActive }) as? UIWindowScene
            if let window = windowScene?.windows.first(where: { $0.isKeyWindow }) {
                return window
            }
        }
        // Fallback for older iOS versions or if no key window is found in the active scene
        // This will still show a warning for iOS 13/14 deployment targets if you don't have a window.
        // If your app's minimum deployment target is iOS 15+, you can remove the fallback.
        return UIApplication.shared.windows.first { $0.isKeyWindow } ?? ASPresentationAnchor() // Fallback for iOS < 15 or if no window found
    }
}
