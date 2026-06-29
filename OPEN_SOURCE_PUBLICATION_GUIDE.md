# Open Source Publication Guide

This document summarizes the steps required to publish LiteLLM Spend Tracker as an open-source project.

## Extension Name

**litellm-spend-tracker**

This name:

- Clearly indicates it works with LiteLLM
- Is searchable and discoverable
- Follows VS Code extension naming conventions
- Describes the primary function (spend tracking)

## Logo

The project logo is located at `extension/resources/logo.svg`.

- **Theme**: Chart/graph with AI brain
- **Colors**: Blue gradient (#4facfe to #00f2fe)
- **Style**: Data visualization focus, emphasizing analytics and the AI/LLM connection

## Pre-Publication Checklist

### 1. Update Publisher Name

```bash
# In extension/package.json
"publisher": "your-actual-github-username"
```

### 2. Update Repository URLs

```bash
# In extension/package.json
"url": "https://github.com/your-username/litellm-spend-tracker"

# In CHANGELOG.md
Update all GitHub URLs
```

### 3. Update Test Extension ID

```bash
# In extension/src/test/suite/extension.test.ts
"your-username.litellm-spend-tracker"
```

### 4. Create GitHub Repository

```bash
cd /path/to/litellm-spend-tracker
git init
git add .
git commit -m "Initial commit: LiteLLM Spend Tracker v1.0.0"
git branch -M main
git remote add origin https://github.com/your-username/litellm-spend-tracker.git
git push -u origin main
```

### 5. Build and Package Extension

```bash
cd extension
npm install
npm run package
# This creates: litellm-spend-tracker-1.0.0.vsix
```

### 6. Publish to VS Code Marketplace

- Create Azure DevOps account (required for marketplace publishing)
- Create Personal Access Token (PAT)
- Install vsce: `npm install -g @vscode/vsce`
- Login: `vsce login your-username`
- Publish: `vsce publish`

## Optional Enhancements

### Add Badges to README

```markdown
![VS Code Marketplace Version](https://img.shields.io/visual-studio-marketplace/v/your-username.litellm-spend-tracker)
![Downloads](https://img.shields.io/visual-studio-marketplace/d/your-username.litellm-spend-tracker)
![License](https://img.shields.io/github/license/your-username/litellm-spend-tracker)
```

### Add Screenshots

- Take screenshots of the extension in action
- Add to `extension/resources/screenshots/`
- Reference in README

### Create Demo Video

- Record a short demo (1-2 minutes)
- Upload to YouTube
- Link in README

### Set Up CI/CD

- Add GitHub Actions for testing
- Automate VSIX building
- Automate marketplace publishing on release

## Verification

All internal/company references have been removed from:

- ✅ Source code
- ✅ Documentation
- ✅ Configuration files
- ✅ Test files
- ✅ Build scripts

The project is ready for open-source publication under the MIT License.

## Next Steps

1. Update publisher name and repository URLs
2. Create GitHub repository
3. Build the extension
4. Test the packaged extension
5. Publish to VS Code Marketplace
6. Share with the community!

## Support

For questions about publishing:

- [VS Code Extension Documentation](https://code.visualstudio.com/api)
- [Publishing Extensions Guide](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [VS Code Marketplace](https://marketplace.visualstudio.com/)
