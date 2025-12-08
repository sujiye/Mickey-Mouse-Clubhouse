import SwiftUI

struct RecognitionView: View {
    var body: some View {
        // 识别页面内容，由于相机画面由ViewController管理，这里可以为空或放置其他UI元素
        // 例如，可以放置一个透明的视图，用于接收手势或显示叠加信息
        Color.clear
            .edgesIgnoringSafeArea(.all) // 忽略安全区域，实现全屏
    }
}

struct RecognitionView_Previews: PreviewProvider {
    static var previews: some View {
        RecognitionView()
    }
}