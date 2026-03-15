---
description: Build and run Android version of AI Recipe Generator Flutter app
---
1. Install Rosetta (required for Apple Silicon Macs).
   // turbo
   ```
   sudo softwareupdate --install-rosetta --agree-to-license
   ```
2. Install Android Studio (includes Android SDK and emulator).
   // turbo
   - Download from https://developer.android.com/studio
   - Follow installer prompts.
3. Configure Flutter to use the Android SDK.
   // turbo
   ```
   flutter config --android-sdk $(/usr/libexec/java_home)/../..  # adjust path if needed
   ```
4. Accept Android SDK licenses.
   // turbo
   ```
   yes | $ANDROID_SDK_ROOT/tools/bin/sdkmanager --licenses
   ```
5. Verify Android toolchain with `flutter doctor`.
   // turbo
   ```
   flutter doctor -v
   ```
6. Create an Android emulator (AVD) if none exists.
   // turbo
   ```
   avdmanager create avd -n pixel_xl -k "system-images;android-34;google_apis;x86_64"
   ```
7. Launch the emulator.
   // turbo
   ```
   emulator -avd pixel_xl
   ```
8. Build the APK.
   // turbo
   ```
   flutter build apk --release
   ```
9. Install and run the app on the emulator.
   // turbo
   ```
   flutter install
   flutter run
   ```
10. (Optional) Test on a physical Android device.
    - Enable Developer Options and USB debugging on the device.
    - Connect via USB and run `flutter devices` to confirm.
    - Then `flutter run`.
