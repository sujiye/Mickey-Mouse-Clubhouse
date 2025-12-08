import UIKit
import SwiftUI
import ARKit
import Combine

class ViewController: UIViewController, ObservableObject, ARSessionDelegate {
    private var arView: ARSCNView!
    private var hostingController: UIHostingController<SwiftUINavigationBarView>?
    @Published var selectedTab: SwiftUINavigationBarView.Tab = .recognition {
        didSet {
            updateARSession()
        }
    }

    private func setupARView() {
        self.arView = ARSCNView(frame: view.bounds)
        self.arView.session = ARSession()
        self.arView.session.delegate = self // 设置ARSession的代理
        self.arView.automaticallyUpdatesLighting = true
        self.arView.backgroundColor = .black
        self.arView.debugOptions = [.showFeaturePoints, .showWorldOrigin] // 添加调试选项
        view.insertSubview(self.arView, at: 0)
        self.arView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            self.arView.topAnchor.constraint(equalTo: view.topAnchor),
            self.arView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            self.arView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            self.arView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
    }

    private func setupSwiftUITabView() {
        let swiftUIRootView = SwiftUINavigationBarView(selectedTab: Binding(
            get: { self.selectedTab },
            set: { self.selectedTab = $0 }
        ))
        hostingController = UIHostingController(rootView: swiftUIRootView)
        guard let hostingController = hostingController else { return }

        addChild(hostingController)
        view.addSubview(hostingController.view)
        hostingController.didMove(toParent: self)

        // 设置SwiftUI视图的背景透明，确保AR视图可见
        hostingController.view.backgroundColor = .clear
        hostingController.view.isOpaque = false // 确保视图完全透明
        hostingController.view.translatesAutoresizingMaskIntoConstraints = false

        NSLayoutConstraint.activate([
            hostingController.view.topAnchor.constraint(equalTo: view.topAnchor),
            hostingController.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            hostingController.view.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            hostingController.view.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
    }

    private func updateARSession() {
        if selectedTab == "recognition" {
            // 确保在识别页面时运行ARSession
            let configuration = ARWorldTrackingConfiguration()
            arView.session.run(configuration)
            print("AR Session started for recognition tab.")
        } else {
            // 在其他页面时暂停ARSession
            arView.session.pause()
            print("AR Session paused for settings tab.")
        }
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        self.view.backgroundColor = .clear // 确保ViewController的根视图背景透明
        setupARView()
        setupSwiftUITabView()
        updateARSession() // Initial AR session state
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        // No longer need to run session here, it's handled by updateARSession
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        arView.session.pause()
    }
    // MARK: - ARSessionDelegate

    func session(_ session: ARSession, didFailWithError error: Error) {
        print("AR Session failed: \(error.localizedDescription)")
        // 可以在这里添加用户友好的错误提示
    }

    func session(_ session: ARSession, cameraDidChangeTrackingState camera: ARCamera) {
        switch camera.trackingState {
        case .notAvailable:
            print("AR Tracking State: Not Available")
        case .limited(let reason):
            print("AR Tracking State: Limited - \(reason)")
        case .normal:
            print("AR Tracking State: Normal")
        }
    }
}

