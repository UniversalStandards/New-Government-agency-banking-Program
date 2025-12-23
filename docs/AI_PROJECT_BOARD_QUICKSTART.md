# AI Project Board - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Access the AI Project Board

Navigate to: **http://localhost:5000/projects/ai-board**

Or from the main dashboard:
1. Go to **Projects** menu
2. Click **AI Project Board** button (purple gradient)

### 2. Select a Project

Use the project dropdown to select which project you want to manage.

### 3. Create a Task with AI

Click the **"AI Task Creator"** button:

```
Describe your task in natural language:
"Add authentication to the API with JWT tokens and rate limiting"
```

Click **"Generate Task with AI"** and review:
- ✓ Suggested title
- ✓ Priority level
- ✓ Estimated hours
- ✓ Recommended assignee
- ✓ AI confidence score

Click **"Create Task"** to add it to your board.

## 🎯 Key Features

### Kanban Board
- **5 Columns**: To Do → In Progress → Review → Completed → Blocked
- **Color-coded priorities**: Red (urgent), Orange (high), Yellow (medium), Green (low)
- **Click any task** to see details

### AI Metrics (Top Panel)
- **Completion Rate**: % of tasks completed
- **Weekly Velocity**: Tasks completed per week
- **Project Health**: 0-100 score
- **Est. Completion**: Predicted finish date

### Health Indicator
- **Green**: Excellent (90-100)
- **Blue**: Good (75-89)
- **Yellow**: Fair (60-74)
- **Red**: Poor (< 60)

## 📝 Common Workflows

### Workflow 1: Create a New Feature

```
1. Click "Create Feature" button
2. Enter feature name: "User Profile Page"
3. Enter description: "Allow users to edit their profile information"
4. Click "Generate Tasks"
```

**AI automatically creates 4 tasks**:
- Design and plan
- Implement core functionality  
- Write tests
- Documentation

### Workflow 2: Get Assignment Suggestions

```
1. Click on any unassigned task
2. Click "AI Suggest Assignee" button
3. Review top 5 recommendations with match scores
4. Click "Auto-Assign" to assign to best match
```

### Workflow 3: Break Down Complex Tasks

```
1. Click on a complex task
2. Click "Decompose into Subtasks"
3. Review suggested subtasks
4. Click "Create Subtasks" to generate them
```

### Workflow 4: Monitor Build Progress

```
1. Click "Build Status" button
2. View detailed analytics:
   - Task distribution
   - Time tracking
   - Velocity trends
   - Health indicators
```

## 🔧 API Quick Reference

### Analyze a Task
```bash
curl -X POST http://localhost:5000/api/ai-projects/tasks/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Add search functionality",
    "description": "Implement full-text search with filters"
  }'
```

### Get Build Status
```bash
curl http://localhost:5000/api/ai-projects/projects/{project_id}/build-status
```

### Create Task from Description
```bash
curl -X POST http://localhost:5000/api/ai-projects/tasks/from-description \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Add email notifications for task updates",
    "project_id": "{project_id}",
    "create": true
  }'
```

### Auto-Assign Task
```bash
curl -X POST http://localhost:5000/api/ai-projects/tasks/auto-assign \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "{task_id}"
  }'
```

## 💡 Pro Tips

### 1. **Write Better Task Descriptions**
Include keywords that help AI understand context:
```
❌ "Fix the thing"
✅ "Fix authentication bug in login API endpoint"
```

### 2. **Use Urgency Keywords**
AI recognizes these words:
- **Urgent**: "urgent", "asap", "critical", "emergency"
- **High**: "important", "high", "blocking"
- **Low**: "minor", "low", "later", "nice to have"

### 3. **Include Skills**
Mention technologies for better assignment:
```
"Create React component for user dashboard with TypeScript"
```
AI will prioritize frontend developers with React skills.

### 4. **Review AI Confidence**
- **>80%**: High confidence, safe to accept
- **60-80%**: Moderate confidence, review suggestions
- **<60%**: Low confidence, manual review recommended

### 5. **Track Velocity**
- **< 1.0**: Team may be overloaded
- **1.0 - 3.0**: Healthy pace
- **> 3.0**: Consider adding complexity

## 🎨 UI Elements Explained

### Task Card Colors
- **Red left border**: Urgent priority
- **Orange left border**: High priority
- **Yellow left border**: Medium priority
- **Green left border**: Low priority

### Badges
- **Purple "AI Available"**: Task can use AI features
- **Blue "Assigned"**: Task has assignee
- **Number badges**: Task count per column

### Progress Bar
- **Green**: Health 90-100 (excellent)
- **Blue**: Health 75-89 (good)
- **Yellow**: Health 60-74 (fair)
- **Red**: Health < 60 (poor)

## 🐛 Troubleshooting

### Problem: "No projects available"
**Solution**: Create a project first using standard project management

### Problem: "AI suggestions not accurate"
**Solution**: Provide more detailed descriptions with specific keywords

### Problem: "Can't auto-assign tasks"
**Solution**: Check you have ADMIN or DEPARTMENT_HEAD role

### Problem: "Metrics showing zero"
**Solution**: Add tasks to the project and complete some to generate metrics

### Problem: "Predicted completion shows N/A"
**Solution**: Need at least 1 completed task to calculate velocity

## 📚 Learn More

- **Full Documentation**: See `docs/AI_PROJECT_BOARD.md`
- **API Reference**: All endpoints documented in full docs
- **GitHub Integration**: Check `.github/workflows/project-board-automation.yml`

## 🎯 Next Steps

1. **Create your first AI-generated task**
2. **Try auto-assignment on 3 tasks**
3. **Monitor health score daily**
4. **Review velocity trends weekly**
5. **Optimize based on AI insights**

## 🤖 AI Capabilities

The system uses:
- **Pattern matching** for complexity analysis
- **Keyword recognition** for skill matching
- **Statistical analysis** for time estimation
- **Heuristic scoring** for assignment
- **Trend analysis** for predictions

Not actual machine learning (yet), but effective AI-style automation!

---

**Ready to get started?** Navigate to `/projects/ai-board` and create your first AI-powered task! 🚀
