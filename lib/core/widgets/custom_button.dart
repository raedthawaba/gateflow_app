import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// زر مخصص للنظام
class CustomButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final ButtonStyle? style;
  final TextStyle? textStyle;
  final IconData? icon;
  final bool isLoading;
  final bool isExpanded;
  final Color? backgroundColor;
  final Color? foregroundColor;

  const CustomButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.style,
    this.textStyle,
    this.icon,
    this.isLoading = false,
    this.isExpanded = true,
    this.backgroundColor,
    this.foregroundColor,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isPrimary = backgroundColor == null && foregroundColor == null;

    return SizedBox(
      width: isExpanded ? double.infinity : null,
      height: 50,
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: style ?? _buildButtonStyle(theme, isPrimary),
        child: isLoading
            ? const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                mainAxisSize: isExpanded ? MainAxisSize.max : MainAxisSize.min,
                children: [
                  if (icon != null) ...[
                    Icon(icon, size: 20),
                    const SizedBox(width: 8),
                  ],
                  Text(
                    text,
                    style: textStyle ?? GoogleFonts.cairo(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  ButtonStyle _buildButtonStyle(ThemeData theme, bool isPrimary) {
    final colorScheme = theme.colorScheme;

    return ElevatedButton.styleFrom(
      backgroundColor: isPrimary ? colorScheme.primary : backgroundColor,
      foregroundColor: isPrimary ? Colors.white : foregroundColor,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      textStyle: GoogleFonts.cairo(
        fontSize: 16,
        fontWeight: FontWeight.w600,
      ),
      elevation: isPrimary ? 2 : 0,
    );
  }
}

/// زر ثانوي
class SecondaryButton extends CustomButton {
  SecondaryButton({
    super.key,
    required String text,
    required VoidCallback onPressed,
    IconData? icon,
    bool isLoading = false,
    bool isExpanded = true,
  }) : super(
          text: text,
          onPressed: onPressed,
          icon: icon,
          isLoading: isLoading,
          isExpanded: isExpanded,
          backgroundColor: Colors.transparent,
          foregroundColor: Theme.of(
            (text is! StatefulElement ? (icon as Icon?)?.key : null) 
                ? Theme.of(text as BuildContext)
                : Theme.of(text as BuildContext),
          ).colorScheme.primary,
        );
}

/// زر نصي
class TextActionButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final TextStyle? style;
  final Color? color;

  const TextActionButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.style,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: onPressed,
      child: Text(
        text,
        style: style ?? GoogleFonts.cairo(
          fontSize: 14,
          color: color ?? Theme.of(context).colorScheme.primary,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}

/// زر أيقونة
class IconActionButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onPressed;
  final String? tooltip;
  final Color? color;
  final double size;

  const IconActionButton({
    super.key,
    required this.icon,
    required this.onPressed,
    this.tooltip,
    this.color,
    this.size = 24,
  });

  @override
  Widget build(BuildContext context) {
    return IconButton(
      onPressed: onPressed,
      icon: Icon(icon, size: size, color: color),
      tooltip: tooltip,
    );
  }
}

/// زر_card مخصص للقوائم
class CardButton extends StatelessWidget {
  final String title;
  final String? subtitle;
  final IconData icon;
  final VoidCallback onTap;
  final Color? iconColor;
  final Color? backgroundColor;
  final Widget? trailing;

  const CardButton({
    super.key,
    required this.title,
    this.subtitle,
    required this.icon,
    required this.onTap,
    this.iconColor,
    this.backgroundColor,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: (iconColor ?? Theme.of(context).colorScheme.primary)
                      .withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  icon,
                  size: 28,
                  color: iconColor ?? Theme.of(context).colorScheme.primary,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: GoogleFonts.cairo(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Theme.of(context).colorScheme.onSurface,
                      ),
                    ),
                    if (subtitle != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        subtitle!,
                        style: GoogleFonts.cairo(
                          fontSize: 13,
                          color: Theme.of(context)
                              .colorScheme
                              .onSurface
                              .withOpacity(0.7),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              if (trailing != null) trailing!,
              Icon(
                Icons.arrow_forward_ios,
                size: 18,
                color: Theme.of(context)
                    .colorScheme
                    .onSurface
                    .withOpacity(0.4),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// مجموعة أزرار متجاوبة
class ButtonRow extends StatelessWidget {
  final List<Widget> buttons;
  final MainAxisAlignment alignment;
  final double spacing;

  const ButtonRow({
    super.key,
    required this.buttons,
    this.alignment = MainAxisAlignment.center,
    this.spacing = 12,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: alignment,
      children: buttons.expand((button) {
        return [
          Flexible(child: button),
          if (button != buttons.last) SizedBox(width: spacing),
        ];
      }).toList(),
    );
  }
}

/// شريط تقدم
class ProgressButton extends StatefulWidget {
  final String text;
  final Future<void> Function() onPressed;
  final ButtonStyle? style;
  final Color? progressColor;

  const ProgressButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.style,
    this.progressColor,
  });

  @override
  State<ProgressButton> createState() => _ProgressButtonState();
}

class _ProgressButtonState extends State<ProgressButton> {
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return CustomButton(
      text: widget.text,
      onPressed: _isLoading ? () {} : _executeAction,
      isLoading: _isLoading,
    );
  }

  Future<void> _executeAction() async {
    setState(() => _isLoading = true);
    try {
      await widget.onPressed();
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }
}
