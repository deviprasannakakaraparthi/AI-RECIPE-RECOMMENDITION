import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import '../api/api_service.dart';
import '../models/recipe.dart';
import 'recipe_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  final List<String> _ingredients = [];
  final TextEditingController _inputController = TextEditingController();
  final ApiService _apiService = ApiService();
  final ImagePicker _picker = ImagePicker();

  bool _isLoading = false;
  List<RecipeMatch> _recipes = [];
  String? _errorMessage;

  String _mealType = "Lunch";
  String _cuisine = "Indian";
  String _spiceLevel = "Medium";
  String _foodStyle = "Curry";

  late AnimationController _pulseController;
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _fadeAnimation =
        CurvedAnimation(parent: _fadeController, curve: Curves.easeOut);
    _fadeController.forward();
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _fadeController.dispose();
    _inputController.dispose();
    super.dispose();
  }

  void _addIngredient(String val) {
    final cleaned = val.trim().toLowerCase();
    if (cleaned.isNotEmpty && !_ingredients.contains(cleaned)) {
      setState(() {
        _ingredients.add(cleaned);
        _inputController.clear();
        _errorMessage = null;
      });
    }
  }

  Future<void> _scanImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image == null) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final bytes = await image.readAsBytes();
      final response = await _apiService.analyzeImageBytes(
        bytes,
        image.name,
        mealType: _mealType,
        cuisine: _cuisine,
        spiceLevel: _spiceLevel,
        foodStyle: _foodStyle,
      );

      setState(() {
        _isLoading = false;
        if (response != null && response.success) {
          for (var ing in response.detectedIngredients) {
            if (!_ingredients.contains(ing)) _ingredients.add(ing);
          }
          _recipes = response.recipes;
        } else {
          _errorMessage = "Could not analyze image. Please try again.";
        }
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = "Network error. Is the backend running?";
      });
    }
  }

  Future<void> _generateRecipe() async {
    if (_ingredients.isEmpty) {
      setState(() => _errorMessage = "Add at least one ingredient first!");
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _recipes = [];
    });

    try {
      final result = await _apiService.generateRecipe(
        ingredients: _ingredients,
        mealType: _mealType,
        cuisine: _cuisine,
        spiceLevel: _spiceLevel,
        foodStyle: _foodStyle,
      );

      setState(() {
        _isLoading = false;
        if (result != null && result.success && result.recipes.isNotEmpty) {
          _recipes = result.recipes;
        } else {
          _errorMessage =
              "No recipes found for those ingredients. Try different combinations!";
        }
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage =
            "Connection error. Make sure backend is running on port 8000.";
      });
    }
  }

  void _navigateToDetail(RecipeMatch match) {
    Navigator.push(
      context,
      PageRouteBuilder(
        pageBuilder: (context, animation, secondaryAnimation) =>
            RecipeDetailScreen(recipe: match),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return SlideTransition(
            position: Tween<Offset>(begin: const Offset(1, 0), end: Offset.zero)
                .animate(CurvedAnimation(
                    parent: animation, curve: Curves.easeOutCubic)),
            child: child,
          );
        },
        transitionDuration: const Duration(milliseconds: 400),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > 800;
    final contentWidth = isWide ? 720.0 : double.infinity;

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0D0D1A), Color(0xFF1A1A2E), Color(0xFF16213E)],
            stops: [0.0, 0.5, 1.0],
          ),
        ),
        child: Stack(
          children: [
            // Decorative background orbs
            Positioned(
              top: -80,
              right: -60,
              child: Container(
                width: 250,
                height: 250,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      const Color(0xFFE94560).withOpacity(0.15),
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
            ),
            Positioned(
              bottom: -100,
              left: -80,
              child: Container(
                width: 300,
                height: 300,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      const Color(0xFF0F3460).withOpacity(0.3),
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
            ),
            // Main content
            SafeArea(
              child: Center(
                child: SizedBox(
                  width: contentWidth,
                  child: FadeTransition(
                    opacity: _fadeAnimation,
                    child: SingleChildScrollView(
                      padding: EdgeInsets.symmetric(
                        horizontal: isWide ? 0 : 20,
                        vertical: 24,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const SizedBox(height: 20),
                          _buildHeader(),
                          const SizedBox(height: 36),
                          _buildIngredientInput(),
                          const SizedBox(height: 20),
                          _buildPreferences(),
                          const SizedBox(height: 24),
                          _buildActionButtons(),
                          const SizedBox(height: 28),
                          if (_errorMessage != null) _buildError(),
                          if (_isLoading) _buildLoader(),
                          if (!_isLoading && _recipes.isNotEmpty)
                            _buildRecipeResults(),
                          const SizedBox(height: 40),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Center(
      child: Column(
        children: [
          // Animated logo icon
          AnimatedBuilder(
            animation: _pulseController,
            builder: (context, child) {
              return Transform.scale(
                scale: 1.0 + (_pulseController.value * 0.08),
                child: Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFE94560), Color(0xFFFF6B6B)],
                    ),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFFE94560).withOpacity(0.4),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: const Icon(Icons.restaurant_menu,
                      color: Colors.white, size: 36),
                ),
              );
            },
          ),
          const SizedBox(height: 20),
          ShaderMask(
            shaderCallback: (bounds) => const LinearGradient(
              colors: [Color(0xFFE94560), Color(0xFFFF6B6B), Color(0xFFE94560)],
            ).createShader(bounds),
            child: const Text(
              "Recipe AI",
              style: TextStyle(
                fontSize: 38,
                fontWeight: FontWeight.w800,
                color: Colors.white,
                letterSpacing: 3,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.06),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.white.withOpacity(0.08)),
            ),
            child: const Text(
              "✨ AI-Powered Kitchen Assistant",
              style: TextStyle(
                  color: Colors.white60, fontSize: 13, letterSpacing: 1),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIngredientInput() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.white.withOpacity(0.07),
            Colors.white.withOpacity(0.03),
          ],
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withOpacity(0.1)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.eco,
                  color: const Color(0xFF4CAF50).withOpacity(0.8), size: 20),
              const SizedBox(width: 8),
              const Text(
                "What's in your kitchen?",
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.5,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.06),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.white.withOpacity(0.08)),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _inputController,
                    onSubmitted: _addIngredient,
                    style: const TextStyle(color: Colors.white, fontSize: 15),
                    decoration: const InputDecoration(
                      hintText: "Type an ingredient (e.g. tomato, onion)...",
                      hintStyle: TextStyle(color: Colors.white30, fontSize: 14),
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
                Material(
                  color: Colors.transparent,
                  child: InkWell(
                    onTap: () => _addIngredient(_inputController.text),
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFFE94560), Color(0xFFFF6B6B)],
                        ),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child:
                          const Icon(Icons.add, color: Colors.white, size: 20),
                    ),
                  ),
                ),
              ],
            ),
          ),
          if (_ingredients.isNotEmpty) ...[
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children:
                  _ingredients.map((ing) => _buildIngredientChip(ing)).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildIngredientChip(String ingredient) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFFE94560).withOpacity(0.2),
            const Color(0xFFE94560).withOpacity(0.1),
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE94560).withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            ingredient,
            style: const TextStyle(
                color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500),
          ),
          const SizedBox(width: 6),
          GestureDetector(
            onTap: () => setState(() => _ingredients.remove(ingredient)),
            child: Icon(Icons.close,
                size: 16, color: Colors.white.withOpacity(0.6)),
          ),
        ],
      ),
    );
  }

  Widget _buildPreferences() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.tune, color: Colors.white.withOpacity(0.5), size: 18),
            const SizedBox(width: 8),
            Text(
              "Personalize your meal",
              style: TextStyle(
                color: Colors.white.withOpacity(0.5),
                fontSize: 13,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            _buildDropdown(
                "🍽️ Meal",
                ["Breakfast", "Lunch", "Dinner", "Snack"],
                _mealType,
                (v) => setState(() => _mealType = v!)),
            const SizedBox(width: 10),
            _buildDropdown(
                "🌍 Cuisine",
                ["Indian", "Continental", "Italian", "Chinese"],
                _cuisine,
                (v) => setState(() => _cuisine = v!)),
          ],
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            _buildDropdown("🌶️ Spice", ["Mild", "Medium", "Spicy", "Hot"],
                _spiceLevel, (v) => setState(() => _spiceLevel = v!)),
            const SizedBox(width: 10),
            _buildDropdown(
                "🍲 Style",
                ["Curry", "Dry", "Soup", "Salad", "Juice"],
                _foodStyle,
                (v) => setState(() => _foodStyle = v!)),
          ],
        ),
      ],
    );
  }

  Widget _buildDropdown(String label, List<String> options, String selected,
      Function(String?) onChanged) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.05),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white.withOpacity(0.08)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label,
                style: const TextStyle(fontSize: 11, color: Colors.white38)),
            DropdownButton<String>(
              value: selected,
              isExpanded: true,
              underline: const SizedBox(),
              dropdownColor: const Color(0xFF1A1A2E),
              icon: Icon(Icons.expand_more,
                  color: Colors.white.withOpacity(0.3), size: 20),
              items: options
                  .map((v) => DropdownMenuItem<String>(
                        value: v,
                        child: Text(v,
                            style: const TextStyle(
                                fontSize: 14, color: Colors.white)),
                      ))
                  .toList(),
              onChanged: onChanged,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        // Main CTA button
        Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: _ingredients.isEmpty ? null : _generateRecipe,
            borderRadius: BorderRadius.circular(20),
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 18),
              decoration: BoxDecoration(
                gradient: _ingredients.isEmpty
                    ? LinearGradient(
                        colors: [Colors.grey.shade800, Colors.grey.shade700])
                    : const LinearGradient(
                        colors: [
                          Color(0xFFE94560),
                          Color(0xFFFF6B6B),
                          Color(0xFFE94560)
                        ],
                        begin: Alignment.centerLeft,
                        end: Alignment.centerRight,
                      ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: _ingredients.isEmpty
                    ? []
                    : [
                        BoxShadow(
                          color: const Color(0xFFE94560).withOpacity(0.4),
                          blurRadius: 20,
                          offset: const Offset(0, 8),
                        ),
                      ],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.auto_awesome,
                    color: _ingredients.isEmpty ? Colors.white38 : Colors.white,
                    size: 22,
                  ),
                  const SizedBox(width: 10),
                  Text(
                    "Find Best Recipe",
                    style: TextStyle(
                      color:
                          _ingredients.isEmpty ? Colors.white38 : Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),
        // Scan button
        Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: _scanImage,
            borderRadius: BorderRadius.circular(20),
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 16),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.04),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: const Color(0xFFE94560).withOpacity(0.4),
                  width: 1.5,
                ),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.photo_camera, color: Color(0xFFE94560), size: 22),
                  SizedBox(width: 10),
                  Text(
                    "Upload Food Photo",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildError() {
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.red.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.warning_amber_rounded,
              color: Colors.redAccent, size: 22),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _errorMessage!,
              style: const TextStyle(color: Colors.redAccent, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoader() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 50),
      child: Column(
        children: [
          const SpinKitWave(color: Color(0xFFE94560), size: 40),
          const SizedBox(height: 20),
          Text(
            "AI is cooking up recipes...",
            style:
                TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 14),
          ),
        ],
      ),
    );
  }

  Widget _buildRecipeResults() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              width: 4,
              height: 24,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFFE94560), Color(0xFFFF6B6B)],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(width: 12),
            const Text(
              "AI Recommendations",
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: Colors.white,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFFE94560).withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                "${_recipes.length}",
                style: const TextStyle(
                  color: Color(0xFFE94560),
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        ...List.generate(_recipes.length, (index) {
          return TweenAnimationBuilder<double>(
            tween: Tween(begin: 0.0, end: 1.0),
            duration: Duration(milliseconds: 400 + (index * 150)),
            curve: Curves.easeOutCubic,
            builder: (context, value, child) {
              return Transform.translate(
                offset: Offset(0, 20 * (1 - value)),
                child: Opacity(opacity: value, child: child),
              );
            },
            child: _buildRecipeCard(_recipes[index], index),
          );
        }),
      ],
    );
  }

  Widget _buildRecipeCard(RecipeMatch recipe, int index) {
    final gradients = [
      [const Color(0xFF1E3A5F), const Color(0xFF0F2847)],
      [const Color(0xFF2D1B4E), const Color(0xFF1A0F30)],
      [const Color(0xFF1B3B2F), const Color(0xFF0F2820)],
      [const Color(0xFF3B2D1B), const Color(0xFF28200F)],
    ];
    final colors = gradients[index % gradients.length];

    return GestureDetector(
      onTap: () => _navigateToDetail(recipe),
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: colors,
          ),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.white.withOpacity(0.08)),
          boxShadow: [
            BoxShadow(
              color: colors[0].withOpacity(0.3),
              blurRadius: 16,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFE94560), Color(0xFFFF6B6B)],
                    ),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: const Icon(Icons.restaurant,
                      color: Colors.white, size: 22),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        recipe.title,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                      if (recipe.style != null)
                        Text(
                          recipe.style!,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.white.withOpacity(0.5),
                          ),
                        ),
                    ],
                  ),
                ),
                Icon(Icons.arrow_forward_ios,
                    color: Colors.white.withOpacity(0.3), size: 16),
              ],
            ),
            if (recipe.description != null) ...[
              const SizedBox(height: 12),
              Text(
                recipe.description!,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: Colors.white.withOpacity(0.6),
                  fontSize: 13,
                  height: 1.5,
                ),
              ),
            ],
            const SizedBox(height: 14),
            Row(
              children: [
                if (recipe.prepTime != null)
                  _buildInfoBadge(Icons.timer_outlined, recipe.prepTime!),
                if (recipe.cookTime != null) ...[
                  const SizedBox(width: 8),
                  _buildInfoBadge(
                      Icons.local_fire_department_outlined, recipe.cookTime!),
                ],
                const Spacer(),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFE94560), Color(0xFFFF6B6B)],
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Text(
                    "View Recipe →",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoBadge(IconData icon, String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.08),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: Colors.white54),
          const SizedBox(width: 4),
          Text(text,
              style: const TextStyle(color: Colors.white70, fontSize: 11)),
        ],
      ),
    );
  }
}
