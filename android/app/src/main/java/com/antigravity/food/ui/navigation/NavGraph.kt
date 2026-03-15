package com.antigravity.food.ui.navigation

import androidx.compose.runtime.*
import com.antigravity.food.ui.screens.*
import com.antigravity.food.ui.viewmodel.RecipeViewModel

sealed class Screen(val route: String) {
    object Splash : Screen("splash")
    object Main : Screen("main")
    object Camera : Screen("camera")
    object RecipeDetail : Screen("detail")
}

@Composable
fun RecipeNavGraph(viewModel: RecipeViewModel) {
    var currentScreen by remember { mutableStateOf<Screen>(Screen.Splash) }
    var selectedRecipeName by remember { mutableStateOf("") }

    when (currentScreen) {
        is Screen.Splash -> {
            SplashScreen(onAnimationFinished = {
                currentScreen = Screen.Main
            })
        }
        is Screen.Main -> {
            MainScreen(
                viewModel = viewModel,
                onNavigateToCamera = { currentScreen = Screen.Camera },
                onNavigateToDetail = { recipeName ->
                    selectedRecipeName = recipeName
                    currentScreen = Screen.RecipeDetail
                }
            )
        }
        is Screen.Camera -> {
            CameraScreen(
                viewModel = viewModel,
                onClose = { currentScreen = Screen.Main }
            )
        }
        is Screen.RecipeDetail -> {
            RecipeDetailScreen(
                viewModel = viewModel,
                onBack = { currentScreen = Screen.Main }
            )
        }
    }
}
