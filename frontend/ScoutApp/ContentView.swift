import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            ScannerView()
                .tabItem {
                    Label("Scanner", systemImage: "doc.viewfinder")
                }
            
            APITestView()
                .tabItem {
                    Label("API Test", systemImage: "network")
                }

            StringAPITestView()
                .tabItem {
                    Label("String API", systemImage: "text.bubble")
                }

            DriveProcessorView()
                .tabItem {
                    Label("Google Drive", systemImage: "icloud.and.arrow.down")
                }
            
            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
        }
    }
}

#Preview {
    ContentView()
}
