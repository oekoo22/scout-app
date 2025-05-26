import SwiftUI
import AuthenticationServices

class AuthService: NSObject, ObservableObject {
    @Published var isAuthenticated: Bool = false
    private var authSession: ASWebAuthenticationSession?

    // Ensure this URL points to your running backend
    private let backendURL = URL(string: "http://localhost:8000")!

    func authenticateWithGoogle(completion: @escaping (Bool, Error?) -> Void) {
        guard let authURL = URL(string: "/auth/google", relativeTo: backendURL) else {
            completion(false, NSError(domain: "AuthService", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid auth URL"]))
            return
        }

        // Replace "scoutapp" with your app's actual URL scheme configured in Info.plist
        // This scheme is used by ASWebAuthenticationSession to capture the redirect.
        // Your backend's /auth/google/callback should ideally redirect to something like "scoutapp://auth_success"
        let callbackURLScheme = "scoutapp" 

        self.authSession = ASWebAuthenticationSession(url: authURL, callbackURLScheme: callbackURLScheme) { callbackURL, error in
            if let error = error {
                print("Authentication error: \(error.localizedDescription)")
                if let authError = error as? ASWebAuthenticationSessionError, authError.code == .canceledLogin {
                    print("User cancelled authentication.")
                    completion(false, nil) 
                } else {
                    completion(false, error)
                }
                return
            }
            
            // If callbackURL is successfully received, it means the flow completed.
            // Your backend at /auth/google/callback has set up the server-side session (token.json).
            print("Authentication successful, callback URL: \(callbackURL?.absoluteString ?? "N/A")")
            DispatchQueue.main.async {
                self.isAuthenticated = true
            }
            completion(true, nil)
        }

        authSession?.presentationContextProvider = self
        authSession?.prefersEphemeralWebBrowserSession = true
        authSession?.start()
    }
}

extension AuthService: ASWebAuthenticationPresentationContextProviding {
    func presentationAnchor(for session: ASWebAuthenticationSession) -> ASPresentationAnchor {
        // Attempt to find the key window for presentation.
        // This might need adjustment based on your app's windowing setup, especially with multiple scenes in SwiftUI.
        return UIApplication.shared.connectedScenes
            .filter { $0.activationState == .foregroundActive }
            .compactMap { $0 as? UIWindowScene }
            .first?.windows
            .first { $0.isKeyWindow } ?? ASPresentationAnchor()
    }
}
