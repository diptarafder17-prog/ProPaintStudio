# 🎨 Pro Paint Studio

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![Kivy](https://img.shields.io/badge/Kivy-Cross--platform-green?logo=android&logoColor=white)
![Build](https://img.shields.io/badge/Build-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Pro Paint Studio** is a professional-grade, dark-themed drawing application built with Python and the Kivy framework. It is designed to work seamlessly on both desktop and mobile, featuring a built-in CI/CD pipeline that automatically compiles an Android APK using GitHub Actions.

---

## ✨ Features

*   ✏️ **Multiple Drawing Tools:** Brush, Straight Line, Rectangle, and Circle.
*   ↶ **Undo & ↷ Redo:** Efficient instruction-group based history stacks.
*   🌈 **Color Picker:** Choose any RGBA color for your brush.
*   📏 **Adjustable Brush Size:** Slider control from 1px to 80px.
*   🌙 **Professional Dark UI:** Easy on the eyes, maximizing canvas focus.
*   📱 **Android Ready:** Fully configured `buildozer.spec` and GitHub Actions workflow for cloud APK compilation.

---

## 🚀 How to Download the Android APK

You do not need to install Android Studio or Buildozer on your computer to get the app on your phone. The APK is built automatically in the cloud!

1. Go to the **[Actions](../../actions)** tab at the top of this repository.
2. In the left sidebar, click on **Build Pro Paint APK**.
3. On the right side, click the **Run workflow** dropdown, then click the green **Run workflow** button.
4. Wait about 10–15 minutes for the build server to compile the app.
5. Once a green checkmark appears, click on the workflow run. Scroll down to the **Artifacts** section at the bottom of the page and click **Pro-Paint-Studio-APK** to download your Android app!

---

## 💻 How to Run Locally (Desktop / PC)

If you want to run or edit the app on your computer, follow these steps:

### 1. Clone the repository
```bash
git clone [https://github.com/diptarafder17-prog/ProPaintStudio.git](https://github.com/diptarafder17-prog/ProPaintStudio.git)
cd ProPaintStudio
