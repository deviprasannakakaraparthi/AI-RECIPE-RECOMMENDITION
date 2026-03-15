
package com.antigravity.food.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.LocalDining
import androidx.compose.material.icons.filled.Timer
import androidx.compose.material.icons.filled.ErrorOutline
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.antigravity.food.ui.viewmodel.RecipeViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    viewModel: RecipeViewModel,
    onNavigateToCamera: () -> Unit,
    onNavigateToDetail: (String) -> Unit
) {
    val uiState by viewModel.uiState
    var inputText by remember { mutableStateOf("") }

    val gradientBrush = Brush.verticalGradient(
        colors = listOf(Color(0xFF1A1A2E), Color(0xFF16213E), Color(0xFF0F3460))
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(gradientBrush)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(Modifier.height(48.dp))

            // ─── Header ───────────────────────────────
            Icon(
                imageVector = Icons.Default.AutoAwesome,
                contentDescription = null,
                tint = Color(0xFFE94560),
                modifier = Modifier.size(36.dp)
            )
            Spacer(Modifier.height(8.dp))
            Text(
                text = "Recipe AI",
                style = MaterialTheme.typography.headlineLarge.copy(
                    color = Color.White,
                    fontWeight = FontWeight.ExtraBold,
                    letterSpacing = 2.sp
                )
            )
            Text(
                text = "What's in your kitchen today?",
                style = MaterialTheme.typography.bodyMedium.copy(
                    color = Color(0xFF8B8FA3)
                ),
                modifier = Modifier.padding(top = 4.dp, bottom = 28.dp)
            )

            // ─── Input Card ──────────────────────────
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(24.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.White.copy(alpha = 0.06f)
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
            ) {
                Column(modifier = Modifier.padding(20.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        TextField(
                            value = inputText,
                            onValueChange = { inputText = it },
                            modifier = Modifier.weight(1f),
                            placeholder = {
                                Text("Add ingredient...", color = Color(0xFF5A5E73))
                            },
                            colors = TextFieldDefaults.textFieldColors(
                                containerColor = Color.Transparent,
                                focusedTextColor = Color.White,
                                unfocusedTextColor = Color.White,
                                cursorColor = Color(0xFFE94560),
                                focusedIndicatorColor = Color(0xFFE94560),
                                unfocusedIndicatorColor = Color.Transparent
                            ),
                            singleLine = true
                        )

                        Spacer(Modifier.width(8.dp))

                        IconButton(
                            onClick = {
                                if (inputText.isNotBlank()) {
                                    viewModel.addIngredient(inputText.trim())
                                    inputText = ""
                                }
                            },
                            modifier = Modifier
                                .size(48.dp)
                                .background(
                                    Brush.linearGradient(
                                        listOf(Color(0xFFE94560), Color(0xFFFF6B6B))
                                    ),
                                    CircleShape
                                )
                        ) {
                            Icon(
                                Icons.Default.Search,
                                contentDescription = "Add",
                                tint = Color.White
                            )
                        }
                    }

                    // Ingredient Chips
                    AnimatedVisibility(
                        visible = uiState.ingredients.isNotEmpty(),
                        enter = fadeIn() + expandVertically(),
                        exit = fadeOut() + shrinkVertically()
                    ) {
                        Column {
                            Spacer(Modifier.height(16.dp))
                            LazyRow(
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                items(uiState.ingredients) { ingredient ->
                                    SuggestionChip(
                                        onClick = { viewModel.removeIngredient(ingredient) },
                                        label = {
                                            Text(
                                                ingredient,
                                                color = Color.White,
                                                fontSize = 13.sp
                                            )
                                        },
                                        colors = SuggestionChipDefaults.suggestionChipColors(
                                            containerColor = Color(0xFFE94560).copy(alpha = 0.2f)
                                        ),
                                        border = SuggestionChipDefaults.suggestionChipBorder(
                                            enabled = true,
                                            borderColor = Color(0xFFE94560).copy(alpha = 0.4f),
                                            borderWidth = 1.dp
                                        ),
                                        icon = {
                                            Icon(
                                                Icons.Default.Close,
                                                contentDescription = "Remove",
                                                tint = Color(0xFFE94560),
                                                modifier = Modifier.size(14.dp)
                                            )
                                        }
                                    )
                                }
                            }
                        }
                    }

                    Spacer(Modifier.height(20.dp))

                    // Find Recipes Button
                    Button(
                        onClick = { viewModel.getRecommendation() },
                        enabled = uiState.ingredients.isNotEmpty() && !uiState.isAnalyzing,
                        modifier = Modifier.fillMaxWidth().height(52.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFFE94560),
                            disabledContainerColor = Color(0xFFE94560).copy(alpha = 0.4f)
                        ),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        if (uiState.isAnalyzing) {
                            CircularProgressIndicator(
                                color = Color.White,
                                modifier = Modifier.size(22.dp),
                                strokeWidth = 2.dp
                            )
                            Spacer(Modifier.width(12.dp))
                            Text("Finding Recipes...", fontSize = 15.sp)
                        } else {
                            Icon(
                                Icons.Default.LocalDining,
                                contentDescription = null,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(Modifier.width(8.dp))
                            Text("Find Recipes", fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
                        }
                    }
                }
            }

            Spacer(Modifier.height(20.dp))

            // ─── Preference Selectors ─────────────────
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.White.copy(alpha = 0.04f)
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "Customize Your Recipe",
                        color = Color(0xFF8B8FA3),
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Medium,
                        modifier = Modifier.padding(bottom = 12.dp, start = 4.dp)
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        PreferenceDropdown(
                            label = "Meal",
                            options = listOf("Breakfast", "Lunch", "Dinner", "Snack"),
                            selected = viewModel.mealType.value,
                            onSelected = { viewModel.mealType.value = it },
                            modifier = Modifier.weight(1f)
                        )
                        PreferenceDropdown(
                            label = "Cuisine",
                            options = listOf("North Indian", "South Indian", "Italian", "Chinese", "Continental"),
                            selected = viewModel.cuisine.value,
                            onSelected = { viewModel.cuisine.value = it },
                            modifier = Modifier.weight(1f)
                        )
                    }

                    Spacer(Modifier.height(8.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        PreferenceDropdown(
                            label = "Spice",
                            options = listOf("Mild", "Medium", "Spicy", "Extra Hot"),
                            selected = viewModel.spiceLevel.value,
                            onSelected = { viewModel.spiceLevel.value = it },
                            modifier = Modifier.weight(1f)
                        )
                        PreferenceDropdown(
                            label = "Style",
                            options = listOf("Curry", "Dry Fry", "Stew", "Salad", "Soup", "Dessert", "Beverage"),
                            selected = viewModel.foodStyle.value,
                            onSelected = { viewModel.foodStyle.value = it },
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }

            Spacer(Modifier.height(20.dp))

            // ─── AI Scan Button ───────────────────────
            OutlinedButton(
                onClick = onNavigateToCamera,
                modifier = Modifier.fillMaxWidth().height(52.dp),
                shape = RoundedCornerShape(16.dp),
                border = androidx.compose.foundation.BorderStroke(
                    1.5.dp,
                    Brush.linearGradient(
                        listOf(Color(0xFFE94560), Color(0xFFFF6B6B))
                    )
                )
            ) {
                Icon(
                    Icons.Default.CameraAlt,
                    contentDescription = null,
                    tint = Color(0xFFE94560),
                    modifier = Modifier.size(22.dp)
                )
                Spacer(Modifier.width(10.dp))
                Text(
                    "Scan Ingredients with AI",
                    color = Color.White,
                    fontWeight = FontWeight.Medium,
                    fontSize = 15.sp
                )
            }

            Spacer(Modifier.height(28.dp))

            // ─── Error State ──────────────────────────
            AnimatedVisibility(
                visible = uiState.errorMessage != null,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFF3D1522)
                    )
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.ErrorOutline,
                            contentDescription = null,
                            tint = Color(0xFFFF6B6B),
                            modifier = Modifier.size(24.dp)
                        )
                        Spacer(Modifier.width(12.dp))
                        Text(
                            text = uiState.errorMessage ?: "",
                            color = Color(0xFFFFB4B4),
                            fontSize = 14.sp,
                            modifier = Modifier.weight(1f)
                        )
                        IconButton(onClick = { viewModel.clearError() }) {
                            Icon(
                                Icons.Default.Close,
                                contentDescription = "Dismiss",
                                tint = Color(0xFFFF6B6B),
                                modifier = Modifier.size(18.dp)
                            )
                        }
                    }
                }
                Spacer(Modifier.height(16.dp))
            }

            // ─── Results Section ──────────────────────
            AnimatedVisibility(
                visible = uiState.recipes.isNotEmpty(),
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column(modifier = Modifier.fillMaxWidth()) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.Restaurant,
                            contentDescription = null,
                            tint = Color(0xFFE94560),
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(Modifier.width(8.dp))
                        Text(
                            text = "Chef's Recommendations",
                            color = Color.White,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold
                        )
                    }

                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(16.dp),
                        contentPadding = PaddingValues(bottom = 16.dp)
                    ) {
                        items(uiState.recipes) { recipe ->
                            Card(
                                modifier = Modifier
                                    .width(300.dp)
                                    .clickable {
                                        viewModel.selectRecipe(recipe)
                                        onNavigateToDetail(recipe.title)
                                    },
                                shape = RoundedCornerShape(24.dp),
                                colors = CardDefaults.cardColors(
                                    containerColor = Color(0xFF0F3460).copy(alpha = 0.85f)
                                ),
                                elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
                            ) {
                                Column(modifier = Modifier.padding(20.dp)) {
                                    // Style Badge
                                    recipe.style?.let { style ->
                                        Surface(
                                            color = Color(0xFFE94560).copy(alpha = 0.15f),
                                            shape = RoundedCornerShape(8.dp)
                                        ) {
                                            Text(
                                                text = style,
                                                color = Color(0xFFE94560),
                                                style = MaterialTheme.typography.labelSmall,
                                                fontWeight = FontWeight.Bold,
                                                modifier = Modifier.padding(
                                                    horizontal = 10.dp,
                                                    vertical = 4.dp
                                                )
                                            )
                                        }
                                        Spacer(Modifier.height(12.dp))
                                    }

                                    Text(
                                        text = recipe.title,
                                        color = Color.White,
                                        style = MaterialTheme.typography.titleLarge,
                                        fontWeight = FontWeight.Bold,
                                        maxLines = 2,
                                        overflow = TextOverflow.Ellipsis
                                    )

                                    recipe.description?.let { desc ->
                                        Spacer(Modifier.height(8.dp))
                                        Text(
                                            text = desc,
                                            color = Color(0xFF8B8FA3),
                                            style = MaterialTheme.typography.bodySmall,
                                            maxLines = 2,
                                            overflow = TextOverflow.Ellipsis
                                        )
                                    }

                                    Spacer(Modifier.height(12.dp))

                                    Row(
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                                    ) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Icon(
                                                Icons.Default.Timer,
                                                contentDescription = null,
                                                tint = Color(0xFF8B8FA3),
                                                modifier = Modifier.size(14.dp)
                                            )
                                            Spacer(Modifier.width(4.dp))
                                            Text(
                                                text = recipe.cookTime ?: "30 mins",
                                                color = Color(0xFF8B8FA3),
                                                fontSize = 12.sp
                                            )
                                        }

                                        recipe.ingredients?.let { ings ->
                                            Row(verticalAlignment = Alignment.CenterVertically) {
                                                Icon(
                                                    Icons.Default.LocalDining,
                                                    contentDescription = null,
                                                    tint = Color(0xFF8B8FA3),
                                                    modifier = Modifier.size(14.dp)
                                                )
                                                Spacer(Modifier.width(4.dp))
                                                Text(
                                                    text = "${ings.size} items",
                                                    color = Color(0xFF8B8FA3),
                                                    fontSize = 12.sp
                                                )
                                            }
                                        }
                                    }

                                    if (!recipe.videoLink.isNullOrEmpty()) {
                                        Spacer(Modifier.height(12.dp))
                                        Text(
                                            text = "▶ Video Demo Available",
                                            color = Color(0xFF4CAF50),
                                            fontSize = 12.sp,
                                            fontWeight = FontWeight.SemiBold
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }

            Spacer(Modifier.height(32.dp))
        }
    }
}

@Composable
fun PreferenceDropdown(
    label: String,
    options: List<String>,
    selected: String,
    onSelected: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }

    Box(modifier = modifier) {
        Button(
            onClick = { expanded = true },
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.White.copy(alpha = 0.08f)
            ),
            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 8.dp),
            shape = RoundedCornerShape(12.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    label,
                    fontSize = 10.sp,
                    color = Color(0xFF8B8FA3),
                    fontWeight = FontWeight.Medium
                )
                Spacer(Modifier.height(2.dp))
                Text(
                    selected,
                    fontSize = 13.sp,
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }
        }
        DropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false },
            modifier = Modifier.background(Color(0xFF1A1A2E))
        ) {
            options.forEach { option ->
                DropdownMenuItem(
                    text = {
                        Text(
                            option,
                            color = if (option == selected) Color(0xFFE94560) else Color.White,
                            fontWeight = if (option == selected) FontWeight.Bold else FontWeight.Normal
                        )
                    },
                    onClick = {
                        onSelected(option)
                        expanded = false
                    }
                )
            }
        }
    }
}
