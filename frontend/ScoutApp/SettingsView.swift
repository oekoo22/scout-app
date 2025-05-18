import SwiftUI

class OpenAISettings: ObservableObject {
    @Published var apiKey: String {
        didSet {
            UserDefaults.standard.set(apiKey, forKey: "openai_api_key")
        }
    }
    
    @Published var baseURL: String {
        didSet {
            UserDefaults.standard.set(baseURL, forKey: "openai_base_url")
        }
    }
    
    init() {
        self.apiKey = UserDefaults.standard.string(forKey: "openai_api_key") ?? ""
        self.baseURL = UserDefaults.standard.string(forKey: "openai_base_url") ?? "https://api.openai.com/v1"
    }
}

struct SettingsView: View {
    @StateObject private var settings = OpenAISettings()
    @State private var isShowingApiKey = false
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("OpenAI Configuration")) {
                    if isShowingApiKey {
                        TextField("API Key", text: $settings.apiKey)
                    } else {
                        SecureField("API Key", text: $settings.apiKey)
                    }
                    
                    Button(action: {
                        isShowingApiKey.toggle()
                    }) {
                        Label(
                            isShowingApiKey ? "Hide API Key" : "Show API Key",
                            systemImage: isShowingApiKey ? "eye.slash" : "eye"
                        )
                    }
                    
                    TextField("Base URL", text: $settings.baseURL)
                }
                
                Section(header: Text("About")) {
                    HStack {
                        Text("Version")
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.gray)
                    }
                }
            }
            .navigationTitle("Settings")
        }
    }
}

#Preview {
    SettingsView()
}
