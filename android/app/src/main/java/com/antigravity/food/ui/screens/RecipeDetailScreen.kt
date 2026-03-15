package com.antigravity.food.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.LocalDining
import androidx.compose.material.icons.filled.Timer
import androidx.compose.material.icons.filled.Whatshot
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.antigravity.food.ui.viewmodel.RecipeViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecipeDetailScreen(
    viewModel: RecipeViewModel,
    onBack: () -> Unit
) {
    val uiState = viewModel.uiState.value
    val recipe = uiState.selectedRecipe
    val recipeName = recipe?.title ?: "Unknown Recipe"
    val instructions = recipe?.instructions ?: emptyList()
    val ingredients = recipe?.ingredients ?: emptyList()

    val gradientBrush = Brush.verticalGradient(
        colors = listOf(Color(0xFF1A1A2E), Color(0xFF16213E), Color(0xFF0F3460))
    )

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Recipe Details",
                        color = Color.White,
                        fontWeight = FontWeight.SemiBold
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.Default.ArrowBack,
                            contentDescription = "Back",
                            tint = Color.White
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color(0xFF1A1A2E)
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(gradientBrush)
                .verticalScroll(rememberScrollState())
                .padding(20.dp)
        ) {
            // ─── Recipe Header Card ────────────────────
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(24.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.White.copy(alpha = 0.06f)
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
            ) {
                Column(modifier = Modifier.padding(24.dp)) {
                    // Style Tag
                    recipe?.style?.let {
                        Surface(
                            color = Color(0xFFE94560).copy(alpha = 0.15f),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text(
                                text = it.uppercase(),
                                style = MaterialTheme.typography.labelSmall,
                                color = Color(0xFFE94560),
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
                            )
                        }
                        Spacer(Modifier.height(12.dp))
                    }

                    Text(
                        text = recipeName,
                        style = MaterialTheme.typography.headlineMedium.copy(
                            color = Color.White,
                            fontWeight = FontWeight.ExtraBold
                        )
                    )

                    recipe?.description?.let { desc ->
                        Spacer(Modifier.height(8.dp))
                        Text(
                            text = desc,
                            color = Color(0xFF8B8FA3),
                            style = MaterialTheme.typography.bodyMedium,
                            lineHeight = 22.sp
                        )
                    }

                    Spacer(Modifier.height(16.dp))

                    // Info Badges Row
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        DetailBadge(
                            icon = Icons.Default.Timer,
                            text = recipe?.cookTime ?: "30m"
                        )
                        if (recipe?.prepTime != null) {
                            DetailBadge(
                                icon = Icons.Default.Timer,
                                text = "Prep: ${recipe.prepTime}"
                            )
                        }
                    }

                    // Video Tutorial Button
                    if (!recipe?.videoLink.isNullOrEmpty()) {
                        val uriHandler = androidx.compose.ui.platform.LocalUriHandler.current
                        Spacer(Modifier.height(16.dp))
                        Button(
                            onClick = { uriHandler.openUri(recipe!!.videoLink!!) },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFFFF0000)
                            ),
                            modifier = Modifier.fillMaxWidth().height(48.dp),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Icon(
                                Icons.Default.PlayArrow,
                                contentDescription = null,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(Modifier.width(8.dp))
                            Text(
                                "Watch Video Tutorial",
                                color = Color.White,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                }
            }

            // ─── Ingredients Section ────────────────────
            if (ingredients.isNotEmpty()) {
                Spacer(Modifier.height(24.dp))

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.LocalDining,
                        contentDescription = null,
                        tint = Color(0xFFE94560),
                        modifier = Modifier.size(22.dp)
                    )
                    Spacer(Modifier.width(8.dp))
                    Text(
                        text = "Ingredients",
                        style = MaterialTheme.typography.titleLarge.copy(
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                    )
                    Spacer(Modifier.width(8.dp))
                    Surface(
                        color = Color(0xFFE94560).copy(alpha = 0.15f),
                        shape = CircleShape
                    ) {
                        Text(
                            text = "${ingredients.size}",
                            color = Color(0xFFE94560),
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                        )
                    }
                }

                Spacer(Modifier.height(12.dp))

                // Separate user ingredients vs additional AI-suggested
                val userIngredients = ingredients.filter { !it.contains("(additional)", ignoreCase = true) }
                val additionalIngredients = ingredients.filter { it.contains("(additional)", ignoreCase = true) }

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = Color.White.copy(alpha = 0.04f)
                    )
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        // Your Ingredients header
                        if (additionalIngredients.isNotEmpty()) {
                            Text(
                                text = "✅ Your Ingredients",
                                color = Color(0xFF4CAF50),
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(bottom = 8.dp)
                            )
                        }

                        userIngredients.forEach { ingredient ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 6.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    Icons.Default.CheckCircle,
                                    contentDescription = null,
                                    tint = Color(0xFF4CAF50),
                                    modifier = Modifier.size(18.dp)
                                )
                                Spacer(Modifier.width(12.dp))
                                Text(
                                    text = ingredient,
                                    color = Color(0xFFD0D3E0),
                                    fontSize = 15.sp
                                )
                            }
                        }

                        // Additional AI-suggested ingredients
                        if (additionalIngredients.isNotEmpty()) {
                            Spacer(Modifier.height(12.dp))
                            Divider(color = Color.White.copy(alpha = 0.08f))
                            Spacer(Modifier.height(12.dp))

                            Text(
                                text = "🛒 AI Suggested (you may need to buy)",
                                color = Color(0xFFFF9800),
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(bottom = 8.dp)
                            )

                            additionalIngredients.forEach { ingredient ->
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(vertical = 6.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Surface(
                                        color = Color(0xFFFF9800).copy(alpha = 0.2f),
                                        shape = CircleShape,
                                        modifier = Modifier.size(18.dp)
                                    ) {
                                        Box(contentAlignment = Alignment.Center) {
                                            Text(
                                                "+",
                                                color = Color(0xFFFF9800),
                                                fontSize = 13.sp,
                                                fontWeight = FontWeight.Bold
                                            )
                                        }
                                    }
                                    Spacer(Modifier.width(12.dp))
                                    Text(
                                        text = ingredient
                                            .replace("(additional)", "")
                                            .replace("(Additional)", "")
                                            .trim(),
                                        color = Color(0xFFFFCC80),
                                        fontSize = 15.sp
                                    )
                                }
                            }
                        }
                    }
                }
            }

            // ─── Instructions Section ────────────────────
            Spacer(Modifier.height(24.dp))

            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Default.Whatshot,
                    contentDescription = null,
                    tint = Color(0xFFE94560),
                    modifier = Modifier.size(22.dp)
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    text = "Instructions",
                    style = MaterialTheme.typography.titleLarge.copy(
                        color = Color.White,
                        fontWeight = FontWeight.Bold
                    )
                )
            }

            Spacer(Modifier.height(12.dp))

            if (instructions.isEmpty()) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = Color.White.copy(alpha = 0.04f)
                    )
                ) {
                    Text(
                        "No instructions available.",
                        color = Color(0xFF8B8FA3),
                        modifier = Modifier.padding(16.dp)
                    )
                }
            } else {
                instructions.forEachIndexed { index, step ->
                    InstructionStep(index + 1, step)
                }
            }

            // ─── Nutrition & Serving ─────────────────────
            if (recipe?.nutrition != null || recipe?.servingSuggestion != null) {
                Spacer(Modifier.height(24.dp))

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFF0F3460).copy(alpha = 0.5f)
                    )
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        recipe.nutrition?.let { nutrition ->
                            Row(verticalAlignment = Alignment.Top) {
                                Icon(
                                    Icons.Default.Whatshot,
                                    contentDescription = null,
                                    tint = Color(0xFFFF9800),
                                    modifier = Modifier.size(18.dp)
                                )
                                Spacer(Modifier.width(10.dp))
                                Column {
                                    Text(
                                        "Nutrition",
                                        color = Color.White,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 14.sp
                                    )
                                    Text(
                                        nutrition,
                                        color = Color(0xFF8B8FA3),
                                        fontSize = 13.sp,
                                        lineHeight = 20.sp
                                    )
                                }
                            }
                        }

                        if (recipe.nutrition != null && recipe.servingSuggestion != null) {
                            Spacer(Modifier.height(16.dp))
                            Divider(color = Color.White.copy(alpha = 0.1f))
                            Spacer(Modifier.height(16.dp))
                        }

                        recipe.servingSuggestion?.let { suggestion ->
                            Row(verticalAlignment = Alignment.Top) {
                                Icon(
                                    Icons.Default.Info,
                                    contentDescription = null,
                                    tint = Color(0xFF4CAF50),
                                    modifier = Modifier.size(18.dp)
                                )
                                Spacer(Modifier.width(10.dp))
                                Column {
                                    Text(
                                        "Serving Suggestion",
                                        color = Color.White,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 14.sp
                                    )
                                    Text(
                                        suggestion,
                                        color = Color(0xFF8B8FA3),
                                        fontSize = 13.sp,
                                        lineHeight = 20.sp
                                    )
                                }
                            }
                        }
                    }
                }
            }

            Spacer(Modifier.height(48.dp))
        }
    }
}

@Composable
fun DetailBadge(icon: ImageVector, text: String) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .background(
                Color.White.copy(alpha = 0.08f),
                RoundedCornerShape(12.dp)
            )
            .padding(horizontal = 14.dp, vertical = 8.dp)
    ) {
        Icon(
            icon,
            contentDescription = null,
            tint = Color(0xFFE94560),
            modifier = Modifier.size(16.dp)
        )
        Spacer(Modifier.width(8.dp))
        Text(text = text, color = Color.White, fontSize = 14.sp)
    }
}

@Composable
fun InstructionStep(number: Int, text: String) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.04f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.Top
        ) {
            // Step Number Circle
            Surface(
                modifier = Modifier.size(32.dp),
                color = Color(0xFFE94560).copy(alpha = 0.15f),
                shape = CircleShape,
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(
                        text = "$number",
                        color = Color(0xFFE94560),
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp
                    )
                }
            }
            Spacer(Modifier.width(14.dp))
            Text(
                text = text,
                color = Color(0xFFD0D3E0),
                fontSize = 15.sp,
                lineHeight = 24.sp,
                modifier = Modifier.weight(1f)
            )
        }
    }
}
