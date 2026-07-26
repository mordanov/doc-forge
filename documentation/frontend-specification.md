# Prompt for GitHub Spec Kit / Claude Code

You are an expert Staff Software Architect, Senior UX Designer, Senior Frontend Engineer, and Product Designer.

Your task is to design and implement the **frontend application** for the DocForge project.

The backend architecture already exists and is defined by the accompanying **Constitution** and **Specification** documents.

Your implementation MUST fully comply with both documents.

The frontend is expected to be production-ready.

---

# Product Overview

DocForge is an AI-assisted editorial publishing platform.

Users upload a Microsoft Word document.

The application transforms it into a professionally designed publication using deterministic rendering and AI-assisted editorial decisions.

The frontend is responsible only for the user experience.

It never performs rendering itself.

All rendering is delegated to the backend.

---

# Objective

Design and implement a modern frontend that looks comparable to products such as:

* Notion
* Linear
* Figma
* Vercel Dashboard
* GitHub
* Raycast
* Arc Browser

The UI should feel clean, modern, elegant and professional.

Avoid enterprise-looking forms.

Avoid Bootstrap-like layouts.

Prefer spacious layouts with excellent typography.

---

# Technology Requirements

Use:

* React 19
* TypeScript
* Vite
* TailwindCSS
* shadcn/ui
* React Hook Form
* Zod
* TanStack Query
* React Router
* Lucide Icons
* Framer Motion
* Zustand
* Recharts (where applicable)

The project must follow modern React best practices.

---

# UI Design Principles

The interface should:

* feel premium
* minimise visual noise
* require minimal learning
* work well on 13" laptops
* support responsive layouts
* support Dark Mode
* support Light Mode
* use subtle animations
* use accessible colour palettes

The interface should look closer to Apple than Microsoft Office.

---

# Information Architecture

The application consists of five main pages.

---

## 1. Home

Landing page.

Contains:

* application logo
* project description
* recent projects
* quick actions
* drag-and-drop upload area

Primary CTA:

"Create Publication"

---

## 2. New Project

Wizard-style interface.

Steps:

1. Upload document

2. Analyse document

3. Configure publication

4. Preview

5. Generate

Display progress during every stage.

---

## 3. Projects

List previously created publications.

Each card contains:

* project name
* created date
* template
* language
* AI model
* rendering status
* output formats

Actions:

* Open
* Duplicate
* Download
* Delete

---

## 4. Settings

Global application settings.

---

## 5. About

Contains:

* version
* documentation
* licences
* contributors
* GitHub repository

---

# New Project Wizard

The wizard is the primary feature of the application.

Each step occupies the full page.

Never present the user with a giant form.

---

# Step 1

## Upload

Support drag-and-drop.

Display:

* filename
* pages
* images
* tables
* headings
* estimated complexity

---

# Step 2

## AI Configuration

Group:

### AI Provider

Only:

OpenAI

---

### AI Model

Dropdown.

Initially include:

* GPT-5.6
* GPT-5.6-mini
* GPT-5.6-sol
* GPT-5.5

Architecture must support future additions.

---

### AI Quality

Segmented control.

Options:

* Fast
* Balanced
* Maximum Quality

---

### Creativity

Slider.

Range:

1–10

Description updates dynamically.

1:

Conservative formatting.

10:

Highly creative editorial design.

---

# Step 3

## Publication Configuration

Organise settings into collapsible cards.

---

### Theme

Dropdown.

Include:

* Minimal
* Modern
* Classic
* National Geographic
* Lonely Planet
* DK Eyewitness
* Magazine
* Corporate
* Luxury
* Academic
* Pop Art
* Scandinavian
* Vintage
* Newspaper
* Children
* Travel Blog

Each option should display:

* preview image
* short description

---

### Output Format

Multi-select.

Options:

* DOCX
* PDF
* DOCX + PDF
* HTML
* Markdown
* EPUB

---

### Language

Dropdown.

Options:

* Auto Detect
* Russian
* English
* Spanish
* German
* French

---

### Image Policy

Options:

* Automatically search photographs
* Replace placeholders only
* Preserve existing images
* Disable image insertion

---

### Image Sources

Checkboxes.

Include:

* Wikimedia Commons
* Official Sources
* Unsplash
* Pexels

---

### Image Density

Slider.

Options:

* Minimal
* Balanced
* Illustrated
* Maximum

---

### Layout Density

Segmented control.

* Compact
* Balanced
* Spacious

---

### Typography

Dropdown.

* Conservative
* Editorial
* Magazine
* Luxury

---

### Colour Palette

Dropdown.

* Auto
* Earth
* Olive
* Blue
* Warm
* Monochrome
* Custom

When Custom is selected, display colour picker.

---

### Sidebar Style

Dropdown.

* None
* Minimal
* Editorial
* Magazine

---

### Cover Page

Dropdown.

* Auto
* Photo
* Minimal
* Illustration
* None

---

### Table of Contents

Dropdown.

* Generate
* Update Existing
* Keep Existing

---

### Headers and Footers

Dropdown.

* Generate
* Replace Existing
* Keep Existing

---

### Validation Level

Dropdown.

* Fast
* Standard
* Strict

---

### AI Explainability

Dropdown.

* Off
* Brief
* Detailed

---

### Offline Mode

Toggle.

---

# Step 4

## Preview

Show a dashboard.

Display estimated:

* rendering time
* AI cost
* number of AI requests
* number of downloaded images
* estimated page count
* inserted photographs
* generated captions
* generated appendix
* cover page
* table of contents

Display warnings.

Display validation summary.

Display licence summary.

---

# Step 5

## Rendering

Display beautiful progress.

Stages:

* Uploading
* Analysing
* AI Processing
* Searching Images
* Downloading Images
* Rendering
* Validation
* Export
* Finished

Each stage has:

* icon
* progress
* elapsed time

---

# Presets

Provide built-in presets.

Examples:

* Travel Guide
* Book
* Magazine
* Academic Paper
* Annual Report
* Corporate Report
* Newsletter

Selecting a preset automatically configures every option.

The user may customise settings afterwards.

---

# Advanced Settings

Hide inside an expandable section.

Include:

* Prompt Version
* Theme Version
* Parallel Downloads
* Retry Count
* Timeout
* Cache Location
* Cache Size
* Maximum AI Requests

---

# UX Requirements

The application should require no more than five minutes to understand.

Every setting includes:

* tooltip
* short explanation

Advanced settings remain hidden by default.

---

# Visual Components

Implement reusable components.

Examples:

* Cards
* Wizard
* Upload Area
* Progress Timeline
* Cost Card
* Statistics Card
* Preview Card
* Settings Card
* Theme Gallery
* Preset Selector

---

# Icons

Use Lucide icons consistently.

Avoid emojis.

---

# Animations

Use Framer Motion.

Animations should be subtle.

Never distract from content.

---

# Accessibility

Comply with WCAG AA.

Keyboard navigation required.

Visible focus indicators required.

Support screen readers.

---

# State Management

Use Zustand.

Keep global state minimal.

Prefer local component state where appropriate.

---

# Forms

Use:

React Hook Form

*

Zod validation

Every form must provide immediate validation feedback.

---

# Code Quality

Follow:

* Feature-based architecture
* SOLID
* Clean Architecture principles where appropriate
* Strict TypeScript
* Reusable components
* No duplicated logic

---

# Deliverables

Generate:

1. Complete frontend architecture.

2. Folder structure.

3. Design system.

4. Component hierarchy.

5. Routing.

6. State management.

7. API layer.

8. Reusable UI components.

9. Responsive layouts.

10. Dark and Light themes.

11. Production-quality React code.

12. Comprehensive README.

13. Setup instructions.

14. Example screenshots or mockups (if supported).

15. Example API integration.

16. All necessary configuration files.

The result should be a frontend that could realistically serve as the public UI for a commercial SaaS product.
