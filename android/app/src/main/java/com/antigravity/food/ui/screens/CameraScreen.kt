package com.antigravity.food.ui.screens

import android.content.Context
import android.util.Log
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Camera
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.FlashOn
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.antigravity.food.ui.viewmodel.RecipeViewModel
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

@Composable
fun CameraScreen(
    viewModel: RecipeViewModel,
    onClose: () -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraExecutor = remember { Executors.newSingleThreadExecutor() }
    
    var imageCapture: ImageCapture? by remember { mutableStateOf(null) }
    
    // Scan line animation
    val infiniteTransition = rememberInfiniteTransition()
    val scanY by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        )
    )

    Box(modifier = Modifier.fillMaxSize().background(Color.Black)) {
        // Camera Preview
        AndroidView(
            factory = { ctx ->
                val previewView = PreviewView(ctx)
                val cameraProviderFuture = ProcessCameraProvider.getInstance(ctx)
                
                cameraProviderFuture.addListener({
                    val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()
                    
                    val preview = Preview.Builder().build().also {
                        it.setSurfaceProvider(previewView.surfaceProvider)
                    }
                    
                    imageCapture = ImageCapture.Builder().build()
                    
                    val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
                    
                    try {
                        cameraProvider.unbindAll()
                        cameraProvider.bindToLifecycle(
                            lifecycleOwner, cameraSelector, preview, imageCapture
                        )
                    } catch (exc: Exception) {
                        Log.e("CameraScreen", "Use case binding failed", exc)
                    }
                }, ContextCompat.getMainExecutor(ctx))
                previewView
            },
            modifier = Modifier.fillMaxSize()
        )

        // Scanning UI Overlay
        Column(modifier = Modifier.fillMaxSize()) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(24.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                IconButton(onClick = onClose, modifier = Modifier.background(Color.Black.copy(alpha = 0.5f), CircleShape)) {
                    Icon(Icons.Default.Close, contentDescription = "Close", tint = Color.White)
                }
                IconButton(onClick = {}, modifier = Modifier.background(Color.Black.copy(alpha = 0.5f), CircleShape)) {
                    Icon(Icons.Default.FlashOn, contentDescription = "Flash", tint = Color.White)
                }
            }

            Spacer(Modifier.weight(1f))

            // Scan Frame
            Box(
                modifier = Modifier
                    .size(300.dp)
                    .align(Alignment.CenterHorizontally)
                    .border(2.dp, Color(0xFFE94560), RoundedCornerShape(24.dp))
            ) {
                // Animated Scan Line
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(2.dp)
                        .offset(y = (300 * scanY).dp)
                        .background(
                            Brush.horizontalGradient(
                                listOf(Color.Transparent, Color(0xFFE94560), Color.Transparent)
                            )
                        )
                )
            }

            Spacer(Modifier.weight(1f))

            // Capture Button
            Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                Button(
                    onClick = {
                        val capture = imageCapture ?: return@Button
                        
                        val photoFile = java.io.File(context.cacheDir, "scan.jpg")
                        val outputOptions = ImageCapture.OutputFileOptions.Builder(photoFile).build()
                        
                        capture.takePicture(
                            outputOptions,
                            ContextCompat.getMainExecutor(context),
                            object : ImageCapture.OnImageSavedCallback {
                                override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                                    val bytes = photoFile.readBytes()
                                    viewModel.analyzeImage(bytes)
                                    onClose()
                                }

                                override fun onError(exception: ImageCaptureException) {
                                    Log.e("CameraScreen", "Capture failed: ${exception.message}", exception)
                                }
                            }
                        )
                    },
                    modifier = Modifier.size(80.dp).clip(CircleShape),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFE94560))
                ) {
                    Icon(Icons.Default.Camera, contentDescription = "Capture", tint = Color.White, modifier = Modifier.size(40.dp))
                }
            }

            Spacer(Modifier.height(48.dp))
        }
    }
}
