import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'dart:js' as js;
import 'package:flutter/foundation.dart';
import '../models/recipe.dart';

class RecipeDetailScreen extends StatelessWidget {
  final RecipeMatch recipe;

  const RecipeDetailScreen({super.key, required this.recipe});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: const Text("Recipe Details",
            style: TextStyle(fontWeight: FontWeight.w700)),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Container(
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0D0D1A), Color(0xFF1A1A2E), Color(0xFF16213E)],
            stops: [0.0, 0.5, 1.0],
          ),
        ),
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 100, 20, 40),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Colors.white.withOpacity(0.08),
                      Colors.white.withOpacity(0.03),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: Colors.white.withOpacity(0.1)),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFFE94560).withOpacity(0.1),
                      blurRadius: 30,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (recipe.style != null)
                      Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 5),
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFFE94560), Color(0xFFFF6B6B)],
                          ),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          recipe.style!,
                          style: const TextStyle(
                              color: Colors.white,
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.5),
                        ),
                      ),
                    Text(
                      recipe.title,
                      style: const TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.w800,
                          letterSpacing: -0.5),
                    ),
                    if (recipe.description != null) ...[
                      const SizedBox(height: 12),
                      Text(
                        recipe.description!,
                        style: TextStyle(
                            color: Colors.white.withOpacity(0.6),
                            fontSize: 14,
                            height: 1.5),
                      ),
                    ],
                    const SizedBox(height: 16),
                    Wrap(
                      spacing: 10,
                      runSpacing: 8,
                      children: [
                        if (recipe.prepTime != null)
                          _buildBadge(Icons.timer_outlined, recipe.prepTime!),
                        if (recipe.cookTime != null)
                          _buildBadge(Icons.local_fire_department_outlined,
                              recipe.cookTime!),
                        if (recipe.nutrition != null)
                          _buildBadge(
                              Icons.monitor_heart_outlined, recipe.nutrition!),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              // Ingredients Section
              _buildSectionHeader("🥘 Ingredients Needed"),
              const SizedBox(height: 14),
              _buildIngredientsGrid(recipe.ingredients),

              const SizedBox(height: 28),

              // Instructions Section
              _buildSectionHeader("👨‍🍳 Cooking Instructions"),
              const SizedBox(height: 16),
              _buildInstructionSteps(recipe.instructions),

              if (recipe.servingSuggestion != null) ...[
                const SizedBox(height: 28),
                _buildSectionHeader("🍽️ Serving Suggestion"),
                const SizedBox(height: 12),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0F3460).withOpacity(0.3),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                        color: const Color(0xFF0F3460).withOpacity(0.4)),
                  ),
                  child: Text(
                    recipe.servingSuggestion!,
                    style: TextStyle(
                        color: Colors.white.withOpacity(0.8),
                        fontSize: 15,
                        height: 1.6),
                  ),
                ),
              ],

              if (recipe.videoLink != null && recipe.videoLink!.isNotEmpty) ...[
                const SizedBox(height: 32),
                Center(
                  child: Container(
                    width: double.infinity,
                    decoration: BoxDecoration(
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFFE94560).withOpacity(0.3),
                          blurRadius: 20,
                          offset: const Offset(0, 8),
                        ),
                      ],
                    ),
                    child: ElevatedButton.icon(
                      onPressed: () async {
                        final String url = recipe.videoLink!;
                        if (kIsWeb) {
                          js.context.callMethod('open', [url, '_blank']);
                        } else {
                          final Uri uri = Uri.parse(url);
                          try {
                            await launchUrl(uri);
                          } catch (e) {
                            debugPrint("Error launching video: $e");
                          }
                        }
                      },
                      icon: const Icon(Icons.play_circle_fill, size: 28),
                      label: const Text(
                        "Watch Recipe Video",
                        style: TextStyle(
                            fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFE94560),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 18),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                        elevation: 0,
                      ),
                    ),
                  ),
                ),
              ],

              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Row(
      children: [
        Container(
          width: 4,
          height: 22,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFFE94560), Color(0xFFFF6B6B)],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 10),
        Text(
          title,
          style: const TextStyle(
              fontSize: 19, fontWeight: FontWeight.w700, color: Colors.white),
        ),
      ],
    );
  }

  Widget _buildBadge(IconData icon, String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
      decoration: BoxDecoration(
        color: const Color(0xFFE94560).withOpacity(0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE94560).withOpacity(0.2)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 15, color: const Color(0xFFE94560)),
          const SizedBox(width: 6),
          Flexible(
            child: Text(
              text,
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w600),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIngredientsGrid(List<String> ingredients) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: ingredients.map((ing) {
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.06),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: Colors.white.withOpacity(0.1)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 6,
                height: 6,
                decoration: const BoxDecoration(
                  color: Color(0xFF4CAF50),
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              Flexible(
                child: Text(
                  ing.trim(),
                  style: TextStyle(
                      color: Colors.white.withOpacity(0.85), fontSize: 14),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildInstructionSteps(List<String> steps) {
    return Column(
      children: List.generate(steps.length, (index) {
        final step = steps[index].trim();
        if (step.isEmpty) return const SizedBox.shrink();

        // Remove leading number/dot if present
        String cleanStep = step;
        final match = RegExp(r'^\d+[\.\)\-]\s*').firstMatch(step);
        if (match != null) {
          cleanStep = step.substring(match.end);
        }

        return Container(
          margin: const EdgeInsets.only(bottom: 14),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.04),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white.withOpacity(0.06)),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 30,
                height: 30,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFFE94560), Color(0xFFFF6B6B)],
                  ),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Center(
                  child: Text(
                    '${index + 1}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 13,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Text(
                  cleanStep,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.85),
                    fontSize: 15,
                    height: 1.6,
                  ),
                ),
              ),
            ],
          ),
        );
      }),
    );
  }
}
