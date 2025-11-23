# Spec Requirements: Tool Handler Guide

## Initial Description
Write a guide for adding new tool handlers.

## Context
This is part of roadmap item 14 (Documentation & Onboarding) - the remaining uncompleted sub-task.

## Requirements Discussion

### First Round Questions

**Q1:** Je suppose que le guide ciblera des développeurs Python intermédiaires/avancés familiers avec Poetry et pytest. Est-ce correct, ou devrait-il être accessible aux débutants Python ?
**Answer:** Accessible aux débutants aussi

**Q2:** Je pense créer un guide pratique de type "tutorial" avec un exemple complet (création d'un handler fictif du début à la fin) plutôt qu'une simple référence API. Cette approche vous convient-elle ?
**Answer:** Oui

**Q3:** Je suppose que le guide devrait couvrir le Protocol ToolHandler, l'enregistrement dans le Registry, le pattern TDD avec pytest, et la structure des fichiers. Y a-t-il d'autres aspects essentiels ?
**Answer:** Ok c'est bon

**Q4:** Le guide devrait-il expliquer comment les handlers sont intégrés dans la commande deploy (usage CLI), ou rester focalisé uniquement sur l'implémentation du handler ?
**Answer:** Les deux

**Q5:** Où devrait se situer ce guide dans la documentation ?
**Answer:** Dans DEVELOPMENT.md. D'ailleurs dans CONTRIBUTING il faudrait faire référence à DEVELOPMENT.md.

**Q6:** Le ContinueToolHandler existant a des fonctionnalités avancées (verification reports, backup/rollback avec sous-répertoires). Le guide devrait-il couvrir une implémentation minimale d'abord puis les fonctionnalités avancées, ou tout inclure dès le départ ?
**Answer:** Tout inclure

### Existing Code to Reference

**Similar Features Identified:**
- Protocol: `src/prompt_unifier/handlers/protocol.py` - ToolHandler Protocol definition
- Reference Implementation: `src/prompt_unifier/handlers/continue_handler.py` - Complete handler example (681 lines)
- Registry: `src/prompt_unifier/handlers/registry.py` - Handler registration system
- Tests: `tests/handlers/` - Test patterns for handlers
- CLI Integration: Need to explore deploy command integration

### Follow-up Questions
None required - all clarifications provided.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A

## Requirements Summary

### Functional Requirements
- Create comprehensive guide in DEVELOPMENT.md for adding new tool handlers
- Make guide accessible to Python beginners while being practical
- Include tutorial-style walkthrough with complete example (fictitious handler)
- Cover the complete ToolHandler Protocol with all required methods
- Explain handler registration in ToolHandlerRegistry
- Document TDD approach with pytest patterns
- Include all advanced features (verification reports, backup/rollback, subdirectory support)
- Explain CLI integration with deploy command
- Update CONTRIBUTING.md to reference DEVELOPMENT.md

### Scope Boundaries
**In Scope:**
- Complete tutorial for creating a new tool handler from scratch
- ToolHandler Protocol documentation with all methods
- Registry registration process
- TDD workflow with pytest examples
- Advanced features coverage (verification, backup/rollback)
- CLI/deploy command integration
- Updating CONTRIBUTING.md reference

**Out of Scope:**
- Creating actual new handlers (just the guide)
- Modifying existing handler implementations
- Changes to the Protocol or Registry code

### Technical Considerations
- Guide must be beginner-friendly with clear explanations
- Use ContinueToolHandler as reference implementation
- Follow existing code patterns and conventions
- Include complete code examples that can be copied
- Explain both simple and advanced implementation patterns
