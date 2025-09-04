import { LlamaIndexServer } from "@llamaindex/server";
import http from "http";
import { request as httpRequest } from "node:http";
import { config } from "dotenv";

// Load environment variables
config();

const innerPort = Number(process.env.INNER_PORT || 3001);

new LlamaIndexServer({
	port: innerPort,
	uiConfig: {
		componentsDir: "components",
		layoutDir: "layout",
		llamaDeploy: {
			deployment: "rhoai-ai-feature-sizing",
			workflow: "rfe-builder-workflow"
		},
		starterQuestions: [
			"I want to add dark mode support to our dashboard with user preference persistence",
			"Help me build an RFE for implementing single sign-on (SSO) across our applications",
			"I need to create an RFE for adding real-time notifications to our platform",
			"Build an RFE for implementing a multi-tenant architecture in our SaaS product",
			"Help me create an RFE for migrating our database from MySQL to PostgreSQL",
			"I want to add AI-powered search functionality to our knowledge base",
			"Create an RFE for implementing automated testing pipelines",
			"Edit the architecture document to include more security considerations"
		],
	},
}).start();

const outerPort = Number(process.env.PORT || 3000);

const server = http.createServer((req, res) => {
	// Set custom headers here for every response
	res.setHeader("X-App-Name", "rhoai-frontend");
	res.setHeader("X-App-Version", "0.1.0");
	res.setHeader("X-Server", "Proxy");

	const options = {
		hostname: "localhost",
		port: innerPort,
		path: req.url,
		method: req.method,
		headers: req.headers,
	};

	const proxyReq = httpRequest(options, (proxyRes) => {
		// Modify CSP to allow additional frame-src domains before forwarding
		try {
			const headers = { ...proxyRes.headers } as Record<string, string | string[]>;
			const headerKey = Object.keys(headers).find(
				(k) => k.toLowerCase() === "content-security-policy" || k.toLowerCase() === "content-security-policy-report-only",
			);
			const additionalDomains = (process.env.ADDITIONAL_FRAME_SRC || "https://example.com").split(/[,\s]+/).filter(Boolean);
			if (headerKey && headers[headerKey]) {
				const raw = Array.isArray(headers[headerKey]) ? headers[headerKey][0] : headers[headerKey];
				const directives = raw.split(";").map((s) => s.trim()).filter(Boolean);
				let updated = false;
				for (let i = 0; i < directives.length; i++) {
					if (directives[i].toLowerCase().startsWith("frame-src")) {
						const parts = directives[i].split(/\s+/);
						const seen = new Set(parts.slice(1));
						for (const d of additionalDomains) {
							if (!seen.has(d)) parts.push(d);
						}
						directives[i] = parts.join(" ");
						updated = true;
						break;
					}
				}
				const newCsp = updated ? directives.join("; ") : `${raw}; frame-src ${additionalDomains.join(" ")}`;
				headers[headerKey] = newCsp;
			} else {
				// No CSP header from upstream; set one that permits framing from allowed domains
				const baseFrameSrc = ["'self'", "https://rfe-builder.atlassian.net", ...additionalDomains].join(" ");
				headers["Content-Security-Policy"] = `frame-src ${baseFrameSrc}`;
			}
			// Forward status and possibly modified headers
			res.writeHead(proxyRes.statusCode || 500, headers as any);
		} catch {
			// Fallback: forward as-is
			res.writeHead(proxyRes.statusCode || 500, proxyRes.headers);
		}
		proxyRes.pipe(res, { end: true });
	});

	proxyReq.on("error", () => {
		res.statusCode = 502;
		res.end("Bad Gateway");
	});

	// Pipe incoming body to inner server
	req.pipe(proxyReq, { end: true });
});

server.listen(outerPort, () => {
	console.log(`> Proxy listening at http://localhost:${outerPort} -> http://localhost:${innerPort}`);
});
