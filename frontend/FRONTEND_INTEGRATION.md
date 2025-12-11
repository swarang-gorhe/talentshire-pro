/**
 * Frontend Integration Guide
 * 
 * Complete guide for integrating frontend with backend shared models
 */

# Frontend Integration with Backend Shared Models

## 📦 What's Integrated

The frontend now has complete type safety and integration with the backend shared models:

### 1. **Type Definitions** (`frontend/src/types/api.ts`)
- ✅ Complete TypeScript types mirroring backend models
- ✅ All enums (Language, Difficulty, TestStatus, etc.)
- ✅ Request/response types for all operations
- ✅ Type hints for autocomplete in VS Code

### 2. **API Service Layer** (`frontend/src/services/api.ts`)
- ✅ Centralized API communication
- ✅ Error handling with custom ApiError class
- ✅ Authentication token management
- ✅ Request timeout handling
- ✅ Organized endpoints by domain (tests, assignments, answers, code, reports)

### 3. **Updated Stores** (`frontend/src/store/testStore.ts`)
- ✅ Integrated with shared models
- ✅ Loading states and error handling
- ✅ Async actions for API calls
- ✅ Test creation wizard
- ✅ Test taking functionality

## 🚀 Usage Examples

### Example 1: Fetch All Tests

```typescript
import { useTestStore } from '@/store/testStore';

function TestList() {
  const { tests, isLoading, fetchTests } = useTestStore();

  useEffect(() => {
    fetchTests();
  }, [fetchTests]);

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {tests.map((test) => (
        <div key={test.test_id}>
          <h3>{test.test_name}</h3>
          <p>{test.description}</p>
          <p>Duration: {test.duration_minutes} minutes</p>
        </div>
      ))}
    </div>
  );
}
```

### Example 2: Create a Test

```typescript
import { useTestStore } from '@/store/testStore';

function CreateTest() {
  const { createTest, isLoading } = useTestStore();

  const handleCreate = async () => {
    try {
      const newTest = await createTest({
        test_name: 'JavaScript Fundamentals',
        description: 'Test your JS knowledge',
        duration_minutes: 60,
        total_marks: 100,
        passing_marks: 40,
      });
      console.log('Test created:', newTest);
    } catch (error) {
      console.error('Failed to create test:', error);
    }
  };

  return (
    <button onClick={handleCreate} disabled={isLoading}>
      {isLoading ? 'Creating...' : 'Create Test'}
    </button>
  );
}
```

### Example 3: Submit MCQ Answer

```typescript
import { useTestStore } from '@/store/testStore';

function MCQQuestion({ question, assignmentId }) {
  const { submitMCQAnswer, currentError } = useTestStore();

  const handleSubmit = async (option: 'A' | 'B' | 'C' | 'D') => {
    try {
      await submitMCQAnswer(assignmentId, question.question_id, option);
      console.log('Answer submitted!');
    } catch (error) {
      console.error('Submission failed:', error);
    }
  };

  return (
    <div>
      <p>{question.question_text}</p>
      {['A', 'B', 'C', 'D'].map((option) => (
        <button key={option} onClick={() => handleSubmit(option)}>
          {option}: {question[`option_${option.toLowerCase()}`]}
        </button>
      ))}
      {currentError && <p className="error">{currentError}</p>}
    </div>
  );
}
```

### Example 4: Submit Code

```typescript
import { useTestStore } from '@/store/testStore';
import { LanguageEnum } from '@/types/api';

function CodeEditor({ question, assignmentId }) {
  const { submitCodingAnswer, saveDraft } = useTestStore();
  const [code, setCode] = useState('');

  const handleSubmit = async () => {
    try {
      const submission = await submitCodingAnswer(
        assignmentId,
        question.question_id,
        code,
        LanguageEnum.PYTHON
      );
      console.log('Code submitted:', submission);
    } catch (error) {
      console.error('Submission failed:', error);
    }
  };

  const handleAutoSave = async () => {
    await saveDraft(
      assignmentId,
      question.question_id,
      code,
      LanguageEnum.PYTHON
    );
  };

  return (
    <div>
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        onBlur={handleAutoSave}
        placeholder="Write your code here..."
      />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}
```

### Example 5: Direct API Call (if store not used)

```typescript
import { testApi, assignmentApi } from '@/services/api';

async function directApiCall() {
  try {
    // Get all tests
    const testsResponse = await testApi.getAllTests(1, 10);
    console.log('Tests:', testsResponse.data);

    // Get specific test
    const testResponse = await testApi.getTest('test-123');
    console.log('Test:', testResponse.data);

    // Get candidate assignments
    const assignmentsResponse = await assignmentApi.getCandidateAssignments('candidate-456');
    console.log('Assignments:', assignmentsResponse.data);
  } catch (error) {
    console.error('API Error:', error);
  }
}
```

## 🔌 API Endpoints Reference

### Tests
- `GET /api/tests` - Get all tests (paginated)
- `GET /api/tests/:testId` - Get single test
- `POST /api/tests` - Create test
- `PUT /api/tests/:testId` - Update test
- `DELETE /api/tests/:testId` - Delete test
- `PATCH /api/tests/:testId/publish` - Publish test

### Assignments
- `GET /api/candidates/:candidateId/assignments` - Get candidate's assignments
- `GET /api/assignments/:assignmentId` - Get single assignment
- `POST /api/assignments` - Create assignment
- `PATCH /api/assignments/:assignmentId/start` - Start assignment
- `PATCH /api/assignments/:assignmentId/end` - End assignment

### Answers
- `POST /api/assignments/:assignmentId/answers/mcq` - Submit MCQ answer
- `POST /api/assignments/:assignmentId/answers/coding` - Submit coding answer
- `GET /api/assignments/:assignmentId/answers` - Get all answers

### Code Submission
- `POST /api/assignments/:assignmentId/code/submit` - Submit code
- `POST /api/assignments/:assignmentId/code/draft` - Save draft
- `GET /api/submissions/:submissionId` - Get submission
- `GET /api/submissions/:submissionId/analysis` - Get analysis result

### Reports
- `GET /api/reports/:reportId` - Get report
- `POST /api/reports/:reportId/generate` - Generate report
- `GET /api/candidates/:candidateId/reports` - Get candidate reports

## 🔑 Environment Setup

Create a `.env.local` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Talentshire
VITE_APP_VERSION=1.0.0
```

## 🧪 Testing with the API

### Using the Store (Recommended)

```typescript
import { useTestStore } from '@/store/testStore';

// In your component
const {
  tests,
  isLoading,
  currentError,
  fetchTests,
  createTest,
  deleteTest,
} = useTestStore();

// Call actions
await fetchTests();
const newTest = await createTest({
  test_name: 'My Test',
  description: 'Test description',
  duration_minutes: 60,
});
```

### Direct API Service

```typescript
import api from '@/services/api';

// Make direct API calls
const response = await api.tests.getAllTests();
const test = await api.tests.getTest('test-id');
const newTest = await api.tests.createTest({ /* data */ });
```

## 🔄 Data Flow

```
Frontend Component
    ↓
Zustand Store (useTestStore)
    ↓
API Service (@/services/api)
    ↓
HTTP Request (with auth token)
    ↓
Backend API (FastAPI)
    ↓
Shared Models (Pydantic validation)
    ↓
Database (SQLAlchemy)
    ↓
PostgreSQL
```

## 🛡️ Error Handling

All API calls are wrapped in error handling:

```typescript
try {
  const test = await testApi.getTest('test-id');
  // Use test data
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`API Error ${error.statusCode}:`, error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## 🔐 Authentication

Authentication token is automatically added to all requests:

```typescript
// Token is stored in localStorage
localStorage.setItem('auth_token', 'your-jwt-token');

// Automatically sent with every request
const response = await testApi.getAllTests();
// Header automatically includes: Authorization: Bearer your-jwt-token
```

## 📝 Best Practices

### 1. Use the Store When Possible
```typescript
// ✅ Good - Uses store
const { tests, fetchTests } = useTestStore();

// ❌ Avoid - Direct API call in component
useEffect(() => {
  testApi.getAllTests().then(setTests);
}, []);
```

### 2. Handle Loading and Error States
```typescript
const { isLoading, currentError, fetchTests } = useTestStore();

if (isLoading) return <Spinner />;
if (currentError) return <Error message={currentError} />;
```

### 3. Type Your API Responses
```typescript
import { Test, TestCreate } from '@/types/api';

const createNewTest = (data: TestCreate): Promise<Test> => {
  return useTestStore.getState().createTest(data);
};
```

### 4. Use Enums Instead of Strings
```typescript
import { LanguageEnum, DifficultyEnum } from '@/types/api';

// ✅ Good
const language = LanguageEnum.PYTHON;

// ❌ Avoid
const language = 'python';
```

### 5. Cleanup in Cleanup Function
```typescript
useEffect(() => {
  const fetchData = async () => {
    await useTestStore.getState().fetchTests();
  };
  
  fetchData();

  return () => {
    // Cleanup if needed
  };
}, []);
```

## 🚨 Common Issues

### Issue: API calls not working
**Solution**: Ensure `VITE_API_URL` is set correctly in `.env.local`

### Issue: Authentication token not sent
**Solution**: Check that token is stored in `localStorage` as `auth_token`

### Issue: Type errors in components
**Solution**: Import types from `@/types/api`:
```typescript
import { Test, TestAssignment, LanguageEnum } from '@/types/api';
```

### Issue: Store not persisting
**Solution**: Check that Zustand persist middleware is configured

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `src/types/api.ts` | TypeScript type definitions |
| `src/services/api.ts` | API service layer |
| `src/store/testStore.ts` | Zustand store for tests |
| `src/store/authStore.ts` | Authentication store |
| `src/store/candidateTestStore.ts` | Candidate test state |

## 🔗 Related Documentation

- Backend Models: `../../shared/models.py`
- Model Mapping: `../../shared/MODEL_MAPPING.md`
- Integration Guide: `../../shared/INTEGRATION_GUIDE.md`
- Database Schema: `../../shared/schema.sql`

## ✅ Checklist for Implementation

- [ ] API types imported and used correctly
- [ ] API service imported in components
- [ ] Store actions called in useEffect/event handlers
- [ ] Loading states displayed to user
- [ ] Error states handled and displayed
- [ ] Authentication token available in localStorage
- [ ] Environment variables configured
- [ ] All enum values typed correctly
- [ ] No TypeScript errors in IDE
- [ ] Ready for backend integration

## 🎉 You're Ready!

The frontend is now fully integrated with the backend shared models. Start building your features with type safety and confidence!
