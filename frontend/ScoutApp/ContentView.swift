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

            DriveProcessorView() // New Tab
                .tabItem {
                    Label("Google Drive", systemImage: "icloud.and.arrow.down") // Example icon
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
