import SwiftUI

struct SwiftUINavigationBarView: View {
    @Binding var selectedTab: Tab

    enum Tab: String, CaseIterable, Identifiable {
        var id: String { rawValue }
        case recognition = "识别"
        case settings = "设置"

        var icon: String {
            switch self {
            case .recognition: return "eye.fill"
            case .settings: return "gearshape.fill"
            }
        }
    }

    var body: some View {
        TabView(selection: $selectedTab) {
            RecognitionView()
                .tabItem {
                    Label(Tab.recognition.rawValue, systemImage: Tab.recognition.icon)
                }
                .tag(Tab.recognition)

            SettingsView()
                .tabItem {
                    Label(Tab.settings.rawValue, systemImage: Tab.settings.icon)
                }
                .tag(Tab.settings)
        }
        .background(Color.clear) // 确保TabView背景透明
    }
}

struct SwiftUINavigationBarView_Previews: PreviewProvider {
    @State static var previewTab: SwiftUINavigationBarView.Tab = .recognition
    static var previews: some View {
        SwiftUINavigationBarView(selectedTab: $previewTab)
    }
}