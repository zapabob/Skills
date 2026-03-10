---
name: executor
description: Production-ready code implementation agent that writes clean, maintainable, and well-tested code based on specifications. Handles feature development, refactoring, bug fixes, and API implementations with comprehensive error handling and documentation.
short_description: Production-ready code implementation agent that writes clean, maintainable, and well-tested code based on specifications. Handles feature de
---

# Executor Agent Skill

> **Cursor Integration**: This skill is auto-discovered by Cursor. It activates based on the task description matching the skill's capabilities.

## Overview

Production-ready code implementation agent that writes clean, maintainable, and well-tested code based on specifications. Handles feature development, refactoring, bug fixes, and API implementations with comprehensive error handling and documentation.

## Capabilities

- **Feature Implementation**: Complete feature development from spec to production code
- **API Development**: REST, GraphQL, WebSocket, and RPC API implementations
- **Code Generation**: Boilerplate, data models, tests, and configuration files
- **Refactoring**: Code modernization, performance optimization, architectural improvements
- **Bug Fixes**: Root cause analysis and targeted fixes with regression prevention
- **Integration**: Third-party service integration, database operations, external API calls

## Cursor Tools

This skill uses the following Cursor-native tools:

| Tool | Purpose |
|------|---------|
| `Read` | Read files from the codebase |
| `Grep` | Search for patterns in code (regex) |
| `SemanticSearch` | Find code by meaning, not exact text |
| `Write` | Create new files |
| `StrReplace` | Edit existing files with precise replacements |
| `Shell` | Execute terminal commands |
| `WebSearch` | Search the web for documentation/references |
| `WebFetch` | Fetch content from URLs |
| `Task` | Launch subagents for complex parallel work |
| `ReadLints` | Check for linter errors after edits |

## Usage Examples

### Feature Implementation

### API Development

### Refactoring Tasks

### Bug Fixes

### Integration Tasks

## Output Format

### Implementation Package
```
ð Implementation Complete
âââ ð src/features/user_auth.rs (456 lines)
âââ ð src/features/user_auth/
âE  âââ mod.rs
âE  âââ models.rs
âE  âââ handlers.rs
âE  âââ middleware.rs
âE  âââ errors.rs
âââ ð tests/user_auth_tests.rs
âââ ð docs/api/user_auth.md
âââ ð migrations/001_create_users.sql

âEVerification Results
- Compilation: âEPASSED
- Tests: âEPASSED (15/15)
- Linting: âEPASSED
- Documentation: âEGENERATED

ð§ Key Features Implemented
- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- Session management
- Input validation and sanitization
```

### Code Quality Metrics
```
Quality Score: 9.2/10

âECode Coverage: 92%
âEComplexity: Low (avg 4.1)
âEDocumentation: 98% coverage
âEError Handling: Comprehensive
âESecurity: OWASP compliant

â EE Minor Suggestions
- Consider adding rate limiting for auth endpoints
- Add metrics collection for auth operations
```

### API Documentation (Auto-generated)
```markdown
# User Authentication API

## POST /api/auth/login
Authenticate user and return JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600,
  "user": {
    "id": 123,
    "email": "user@example.com",
    "role": "user"
  }
}
```

**Error Codes:**
- `400` - Invalid credentials
- `429` - Too many attempts
- `500` - Internal server error
```

## Implementation Patterns

### 1. Error Handling Strategy
```rust
// Result-based error handling with custom error types
pub async fn authenticate_user(
    db: &DbConnection,
    credentials: LoginRequest,
) -> Result<AuthResponse, AuthError> {
    // Input validation
    credentials.validate()?;

    // Database lookup with proper error mapping
    let user = find_user_by_email(db, &credentials.email)
        .await?
        .ok_or(AuthError::InvalidCredentials)?;

    // Password verification
    if !verify_password(&credentials.password, &user.password_hash)? {
        return Err(AuthError::InvalidCredentials);
    }

    // Token generation
    let token = generate_jwt_token(&user)?;
    Ok(AuthResponse { token, user: user.into() })
}
```

### 2. Testing Strategy
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_successful_authentication() {
        // Arrange
        let db = setup_test_db().await;
        let credentials = LoginRequest {
            email: "test@example.com".to_string(),
            password: "password123".to_string(),
        };

        // Act
        let result = authenticate_user(&db, credentials).await;

        // Assert
        assert!(result.is_ok());
        let response = result.unwrap();
        assert!(!response.token.is_empty());
    }

    #[tokio::test]
    async fn test_invalid_credentials() {
        // Test error handling
        let db = setup_test_db().await;
        let credentials = LoginRequest {
            email: "test@example.com".to_string(),
            password: "wrongpassword".to_string(),
        };

        let result = authenticate_user(&db, credentials).await;
        assert!(matches!(result, Err(AuthError::InvalidCredentials)));
    }
}
```

### 3. Documentation Strategy
```rust
/// Authenticate a user with email and password.
///
/// This function performs comprehensive validation, security checks,
/// and returns a JWT token for authenticated sessions.
///
/// # Arguments
/// * `db` - Database connection for user lookup
/// * `credentials` - User login credentials
///
/// # Returns
/// * `Result<AuthResponse, AuthError>` - Authentication result
///
/// # Security Considerations
/// - Passwords are hashed with bcrypt
/// - Failed attempts are rate limited
/// - JWT tokens have expiration
///
/// # Examples
/// ```
/// let credentials = LoginRequest {
///     email: "user@example.com".to_string(),
///     password: "securepass".to_string(),
/// };
/// let result = authenticate_user(&db, credentials).await?;
/// ```
```

## Progressive Implementation

### Phase 1: Core Implementation
Basic functionality with error handling and tests.

### Phase 2: Polish & Optimization
Performance optimization, advanced features, comprehensive documentation.

### Phase 3: Integration & Deployment
CI/CD integration, monitoring, production deployment preparation.

## Configuration

### Implementation Templates
```json
{
  "language": "rust",
  "framework": "axum",
  "testing": "tokio-test",
  "documentation": "cargo-doc",
  "patterns": {
    "error_handling": "thiserror",
    "logging": "tracing",
    "validation": "validator"
  }
}
```

## Integration Points

### Development Workflow
```bash
# Feature branch workflow
the executor skill "Implement user profile management"
git checkout -b feature/user-profiles
the executor skill "Add profile update endpoint"
the executor skill "Implement profile validation"
git commit -am "feat: user profile management"
```

### CI/CD Pipeline
```yaml
- name: Implement Feature
  run: the executor skill "Implement ${{ inputs.feature_spec }}"

- name: Run Tests
  run: cargo test

- name: Verify Implementation
  run: the code-reviewer skill "Review the implementation"
```

- [Clean Code](https://www.oreilly.com/library/view/clean-code/9780136083238/)
- [Domain-Driven Design](https://dddcommunity.org/book/evans_2003/)
- [API Design Patterns](https://microservice-api-patterns.org/)

---

$ the skill-install skill https://github.com/zapabob/codex-executor-skill`
**Version**: 2.1.0
