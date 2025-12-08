import SwiftUI

struct SettingsView: View {
    var body: some View {
        NavigationView {
            List {
                Section(header: Text("通用")) {
                    NavigationLink(destination: Text("关于")) {
                        Label("关于", systemImage: "info.circle.fill")
                    }
                    NavigationLink(destination: Text("显示与亮度")) {
                        Label("显示与亮度", systemImage: "sun.max.fill")
                    }
                    NavigationLink(destination: Text("通用设置")) {
                        Label("通用", systemImage: "gearshape.fill")
                    }
                }

                Section(header: Text("隐私与安全")) {
                    NavigationLink(destination: Text("隐私")) {
                        Label("隐私", systemImage: "hand.raised.fill")
                    }
                    NavigationLink(destination: Text("安全")) {
                        Label("安全", systemImage: "lock.fill")
                    }
                }

                Section(header: Text("关于应用")) {
                    HStack {
                        Label("版本", systemImage: "tag.fill")
                        Spacer()
                        Text("1.0.0")
                    }
                    NavigationLink(destination: Text("使用条款")) {
                        Label("使用条款", systemImage: "doc.text.fill")
                    }
                }
            }
            .navigationTitle("设置")
        }
    }
}

struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
    }
}