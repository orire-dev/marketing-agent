#!/bin/bash
# Script to push marketing-agent to GitHub

echo "📦 Pushing marketing-agent to GitHub..."
echo ""

# Check if remote exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "✅ Remote 'origin' already configured"
    git remote -v
else
    echo "Adding remote repository..."
    git remote add origin https://github.com/orire-dev/marketing-agent.git
    echo "✅ Remote added"
fi

echo ""
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🌐 Repository: https://github.com/orire-dev/marketing-agent"
    echo "📄 GitHub Pages: https://orire-dev.github.io/marketing-agent/ (after enabling in settings)"
else
    echo ""
    echo "❌ Push failed. Make sure:"
    echo "  1. Repository exists at https://github.com/orire-dev/marketing-agent"
    echo "  2. You have push access"
    echo "  3. GitHub credentials are configured"
fi
