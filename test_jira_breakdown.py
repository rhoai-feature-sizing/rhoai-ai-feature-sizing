#!/usr/bin/env python3
"""
Test script for JIRA Breakdown Workflow

This script demonstrates how to use the new JIRA breakdown endpoint.
"""

import asyncio
import json
import aiohttp
from typing import Dict, Any


async def test_jira_breakdown_endpoint():
    """Test the JIRA breakdown workflow endpoint"""
    
    # LlamaDeploy API base URL
    base_url = "http://localhost:4501"
    deployment_name = "rhoai-ai-feature-sizing"
    service_name = "jira-breakdown-workflow"
    
    # Test payload
    test_payload = {
        "input": json.dumps({
            "jira_id": "RHOAIENG-669",
            "description": "Additional context: This feature should improve ML model deployment experience",
            "user_id": "test_user",
            "create_jira_items": False  # Set to True to actually create JIRA items
        }),
        "service_id": service_name
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Create a new task
            print("🚀 Creating JIRA breakdown task...")
            create_url = f"{base_url}/deployments/{deployment_name}/tasks/create"
            
            async with session.post(create_url, json=test_payload) as response:
                if response.status != 200:
                    print(f"❌ Failed to create task: {response.status}")
                    print(await response.text())
                    return
                
                task_data = await response.json()
                task_id = task_data["task_id"]
                session_id = task_data.get("session_id")
                
                print(f"✅ Task created: {task_id}")
                print(f"📝 Session ID: {session_id}")
            
            # Stream events to monitor progress
            print("\n📊 Streaming events...")
            events_url = f"{base_url}/deployments/{deployment_name}/tasks/{task_id}/events"
            params = {"raw_event": "true"}
            if session_id:
                params["session_id"] = session_id
            
            async with session.get(events_url, params=params) as response:
                if response.status != 200:
                    print(f"❌ Failed to stream events: {response.status}")
                    return
                
                async for line in response.content:
                    if line:
                        try:
                            event_data = json.loads(line.decode('utf-8'))
                            event_type = event_data.get("type", "unknown")
                            
                            if event_type == "progress":
                                # Handle progress events
                                data = event_data.get("data", {})
                                stage = data.get("stage", "")
                                progress = data.get("progress", 0)
                                message = data.get("message", "")
                                print(f"⏳ [{progress:3d}%] {stage}: {message}")
                            
                            elif event_type == "result":
                                # Handle final result
                                result = event_data.get("data", {})
                                print("\n🎉 JIRA Breakdown Complete!")
                                print_breakdown_summary(result)
                                break
                            
                            elif event_type == "error":
                                print(f"❌ Error: {event_data.get('data', {}).get('message', 'Unknown error')}")
                                break
                                
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            print(f"⚠️  Error processing event: {e}")
                            continue
        
        except Exception as e:
            print(f"❌ Request failed: {e}")


def print_breakdown_summary(result: Dict[str, Any]):
    """Print a formatted summary of the breakdown results"""
    
    print(f"\n📋 Original JIRA: {result.get('original_jira_id', 'N/A')}")
    print(f"📝 Summary: {result.get('original_summary', 'N/A')}")
    print(f"⏱️  Processing Time: {result.get('processing_time', 0):.2f} seconds")
    
    # Print epics
    epics = result.get('epics', [])
    print(f"\n🎯 Epics Generated: {len(epics)}")
    for i, epic in enumerate(epics, 1):
        print(f"  {i}. {epic.get('title', 'Untitled Epic')}")
        print(f"     Components: {', '.join(epic.get('components', []))}")
    
    # Print stories
    stories = result.get('stories', [])
    print(f"\n📚 Stories Generated: {len(stories)}")
    total_points = 0
    
    for i, story in enumerate(stories, 1):
        points = story.get('story_points', 0)
        if points:
            total_points += points
        
        print(f"  {i}. {story.get('title', 'Untitled Story')}")
        print(f"     Points: {points or 'TBD'}, Parent: {story.get('parent_epic', 'None')}")
    
    print(f"\n📊 Total Story Points: {total_points}")
    
    # Print agent analyses summary
    agent_analyses = result.get('agent_analyses', {})
    print(f"\n🤖 Agent Analyses: {len(agent_analyses)} agents contributed")
    for agent in agent_analyses.keys():
        print(f"  • {agent}")
    
    # Print created JIRA items if any
    created_items = result.get('created_jira_items')
    if created_items:
        print(f"\n✅ Created JIRA Items: {len(created_items)}")
        for item in created_items:
            print(f"  • {item}")


async def main():
    """Main test function"""
    print("🧪 JIRA Breakdown Workflow Test")
    print("=" * 50)
    print("\n⚠️  Make sure LlamaDeploy is running:")
    print("   uv run -m llama_deploy.apiserver")
    print("   uv run llamactl deploy deployment.yml")
    print("\n" + "=" * 50)
    
    await test_jira_breakdown_endpoint()


if __name__ == "__main__":
    asyncio.run(main())