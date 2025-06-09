# Frequently Asked Questions (FAQ)

## General Questions

### What is RHOAI AI Feature Sizing?

RHOAI AI Feature Sizing is an AI-powered tool designed to help teams analyze, refine, and estimate software features. It integrates with JIRA to streamline the feature sizing process using artificial intelligence.

### Who should use this tool?

- Product managers planning features
- Development teams estimating work
- Scrum masters managing backlogs
- Anyone involved in feature planning and estimation

### What makes this different from other estimation tools?

Our tool leverages AI (LLaMA Stack) to provide intelligent analysis and suggestions, rather than relying solely on manual input. It also integrates directly with JIRA workflows.

## Installation & Setup

### What are the system requirements?

- Python 3.12 or higher
- Access to LLaMA Stack or compatible AI service
- JIRA instance (for JIRA integration features)
- Minimum 4GB RAM recommended

### Do I need a paid AI service?

While the tool is designed to work with LLaMA Stack, you can configure it to work with various AI services. Some may require paid access depending on usage.

### Can I run this locally without internet?

The tool requires internet access for:
- AI model interactions (unless using local models)
- JIRA API calls
- Package installation

Some features may work offline with proper local setup.

## Usage Questions

### How do I start analyzing a feature?

1. Use the feature refinement stage: `python -m stages.refine_feature --input "your feature"`
2. Or start with a JIRA ticket: `python -m tools.mcp_jira --fetch TICKET-123`
3. Follow the prompts for AI-assisted analysis

### What input formats are supported?

- Plain text feature descriptions
- JIRA ticket IDs
- JSON files with structured feature data
- Markdown files

### How accurate are the AI estimates?

AI estimates should be used as a starting point and refined with human expertise. Accuracy improves with:
- More detailed feature descriptions
- Historical data for context
- Team-specific customization

### Can I customize the AI prompts?

Yes! AI prompts are stored in the `prompts/` directory and can be customized. See [AI Components Documentation](../ai/prompts.md) for details.

## JIRA Integration

### What JIRA permissions do I need?

- Read access to projects you want to analyze
- Write access to create/update tickets
- API token generation permissions

### Which JIRA versions are supported?

The tool works with JIRA Cloud and Server instances that support REST API v2/v3.

### Can I work with multiple JIRA projects?

Yes, configure multiple project keys in your environment variables or specify them per command.

### What happens if JIRA is unavailable?

The tool can work in offline mode for feature analysis. JIRA-specific features will be disabled until connectivity is restored.

## Technical Questions

### How do I add a new processing stage?

1. Create a new Python file in the `stages/` directory
2. Implement the required interface
3. Update the main.py to include the new stage
4. Add documentation in `/docs`

### Can I integrate with other tools besides JIRA?

Yes! The tool architecture supports additional integrations. Create new tools in the `tools/` directory following the MCP pattern.

### How do I contribute prompts for different domains?

- Add domain-specific prompts to the `prompts/` directory
- Follow the existing naming conventions
- Submit a pull request with documentation
- See [Contributing Guide](../../CONTRIBUTING.md)

### What if I encounter a bug?

1. Check this FAQ and documentation first
2. Search existing issues in the repository
3. Create a detailed bug report with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Log files if available

## Troubleshooting

### "ImportError: No module named 'fire'"

Install dependencies:
```bash
uv sync
# or
pip install -r requirements.txt
```

### "Connection refused" errors with AI service

- Check your API endpoint and credentials
- Verify network connectivity
- Ensure the AI service is running and accessible

### JIRA authentication keeps failing

- Verify your API token is correct
- Check JIRA URL format (include https://)
- Ensure your user has necessary permissions
- Test with a simple JIRA API call

### Features seem to hang during processing

- Check AI service response times
- Verify sufficient system resources
- Review logs for error messages
- Try with simpler/shorter feature descriptions

### Where can I find logs?

Currently logs are output to console. For persistent logging:
- Redirect output: `python main.py > output.log 2>&1`
- Or configure Python logging in your environment

## Getting More Help

### Where can I find more documentation?

- [Getting Started Guide](./getting-started.md)
- [Architecture Overview](../architecture/overview.md)
- [API Documentation](../api/endpoints.md)
- [Development Setup](../development/setup.md)

### How do I request a new feature?

1. Check existing feature requests
2. Create a detailed request including:
   - Use case description
   - Expected behavior
   - Benefits to users
3. Submit as an issue in the repository

### Is there a community or support forum?

Check the repository for:
- Issue tracker for bug reports
- Discussions for questions and ideas
- Contributing guidelines for code contributions

---

*Don't see your question here? Feel free to open an issue or start a discussion in the repository.*