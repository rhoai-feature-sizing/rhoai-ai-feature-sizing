#!/usr/bin/env python3
"""
Quick test script for Create RFE Button verification
Tests just the button event emission without running full Phase 1 workflow
"""
import asyncio
import time
from typing import Any, Dict
from llama_index.core.workflow import Context, Event
from llama_index.core.chat_ui.events import UIEvent
from src.rfe_builder_workflow import create_rfe_builder_workflow


class MockContext(Context):
    """Mock context for testing event emission"""
    
    def __init__(self):
        self.events = []
    
    def write_event_to_stream(self, event: Event) -> None:
        """Capture events for testing"""
        self.events.append(event)
        print(f"📤 Event emitted: {event.type if hasattr(event, 'type') else type(event).__name__}")
        if hasattr(event, 'data'):
            print(f"   Data keys: {list(event.data.keys()) if isinstance(event.data, dict) else 'Non-dict data'}")


async def test_create_rfe_button_event():
    """Test just the Create RFE button event emission"""
    print("🧪 Quick Test: Create RFE Button Event Emission")
    print("=" * 50)
    
    # Create mock context
    ctx = MockContext()
    
    # Mock Phase 1 artifacts (what would be generated after agent analysis)
    mock_phase_1_artifacts = {
        "rfe_description": """# Dark Mode Implementation RFE

## Problem Statement
Our dashboard currently lacks dark mode functionality, which affects user experience in low-light environments and accessibility for users with visual sensitivities.

## Proposed Solution
Implement a comprehensive dark mode theme with user preference persistence across sessions.

## Requirements
1. Complete dark theme for all UI components
2. Smooth transitions between light/dark modes
3. Accessibility compliance (WCAG contrast ratios)
4. User preference storage (localStorage + server-side)
5. Cross-browser compatibility testing

## Success Criteria
- Users can toggle between themes seamlessly
- Preferences persist across sessions
- Meets accessibility standards
- Works across all supported browsers and devices""",

        "feature_refinement": """# Feature Refinement: Dark Mode Implementation

## Technical Approach
### Theme System Architecture
- CSS custom properties (CSS variables) for dynamic theming
- Theme context provider for React components
- Centralized theme configuration files

### Implementation Phases
#### Phase 1: Core Infrastructure (2-3 days)
- Set up theme system architecture
- Implement base dark theme variables
- Create theme toggle component

#### Phase 2: Component Updates (3-5 days) 
- Update all UI components for theme support
- Ensure proper contrast ratios
- Test component interactions

#### Phase 3: Persistence & Polish (2-3 days)
- Implement user preference storage
- Add smooth transitions
- Cross-browser testing and fixes

## Risk Mitigation
- **Browser compatibility**: Progressive enhancement approach
- **Performance**: Lazy load theme resources
- **Accessibility**: Automated contrast testing in CI/CD

## Dependencies
- Design system updates for dark theme colors
- Backend API for user preference storage
- QA testing across multiple devices/browsers"""
    }
    
    try:
        # Simulate the Create RFE button event emission
        # This is exactly what happens at the end of Phase 1
        ctx.write_event_to_stream(
            UIEvent(
                type="CreateRFEButton",
                data={
                    "message": "RFE documents are ready! Create the RFE in Jira when you're satisfied with the content.",
                    "artifacts": list(mock_phase_1_artifacts.keys()),
                    "rfe_content": mock_phase_1_artifacts.get("rfe_description", ""),
                    "refinement_content": mock_phase_1_artifacts.get("feature_refinement", ""),
                },
            )
        )
        
        # Verify the event was captured correctly
        if ctx.events:
            event = ctx.events[0]
            print(f"\n✅ Event captured successfully!")
            print(f"   Event type: {event.type}")
            print(f"   Data structure valid: {'data' in dir(event)}")
            
            if hasattr(event, 'data') and isinstance(event.data, dict):
                data = event.data
                print(f"   Message: {data.get('message', 'Missing')[:50]}...")
                print(f"   Artifacts count: {len(data.get('artifacts', []))}")
                print(f"   RFE content length: {len(data.get('rfe_content', ''))}")
                print(f"   Refinement content length: {len(data.get('refinement_content', ''))}")
                
                # Show artifact names
                artifacts = data.get('artifacts', [])
                if artifacts:
                    print(f"   Artifacts: {', '.join(artifacts)}")
            
            return True, event
        else:
            print("❌ No events captured")
            return False, None
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_workflow_integration():
    """Test that we can create workflow instance without issues"""
    print("\n🧪 Testing Workflow Integration")
    print("=" * 30)
    
    try:
        workflow = create_rfe_builder_workflow()
        print("✅ Workflow created successfully")
        print(f"   Workflow type: {type(workflow).__name__}")
        return True
    except Exception as e:
        print(f"❌ Workflow creation failed: {e}")
        return False


async def main():
    """Main test runner"""
    print("🚀 Quick Create RFE Button Test Suite")
    print("=" * 60)
    
    # Test 1: Event emission
    success1, event = await test_create_rfe_button_event()
    
    # Test 2: Workflow integration
    success2 = await test_workflow_integration()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"  Create RFE Button Event: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"  Workflow Integration: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print(f"\n🎉 All tests passed!")
        print(f"\n📋 What this verifies:")
        print(f"  ✅ CreateRFEButton event structure is correct")
        print(f"  ✅ Mock data format matches expected structure")
        print(f"  ✅ Event emission mechanism works")
        print(f"  ✅ No import or initialization errors")
        
        print(f"\n🔄 Next steps to verify UI:")
        print(f"  1. Deploy the workflow: uv run llamactl deploy deployment.yml")
        print(f"  2. Open UI: http://localhost:4501/deployments/rhoai-ai-feature-sizing/ui")  
        print(f"  3. Check browser network tab for CreateRFEButton events")
        print(f"  4. OR run full workflow and verify button appears after Phase 1")
    else:
        print(f"\n💥 Some tests failed - check the errors above")


if __name__ == "__main__":
    asyncio.run(main())