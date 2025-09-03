import { LlamaIndexServer } from "@llamaindex/server";
import { config } from "dotenv";

// Load environment variables
config();

new LlamaIndexServer({
	uiConfig: {
		componentsDir: "components",
		layoutDir: "layout",
		llamaDeploy: {
			deployment: "rhoai-ai-feature-sizing",
			workflow: "rfe-investigation-workflow"
		},
		starterQuestions: [
			"I want to add dark mode support to our dashboard with user preference persistence",
			"Help me investigate an RFE for implementing single sign-on (SSO) across our applications",
			"I need to create an RFE for adding real-time notifications to our platform",
			"Investigate an RFE for implementing a multi-tenant architecture in our SaaS product",
			"Help me develop an RFE for migrating our database from MySQL to PostgreSQL",
			"I want to add AI-powered search functionality to our knowledge base",
			"Investigate an RFE for implementing automated testing pipelines",
			"Generate artifacts for my completed RFE document"
		],
	},
}).start();
