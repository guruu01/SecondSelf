# SecondSelf — Edge Cases and Corner Scenarios

## Overview

This document catalogs all edge cases, corner scenarios, and exceptional conditions that may occur in the SecondSelf system. Each edge case includes description, impact, detection method, and mitigation strategy.

**Purpose**: Ensure robust error handling and graceful degradation across all system components
**Scope**: All 4 phases of the project (Capture, Classify, Visualize, Query)
**Maintenance**: Update as new edge cases are discovered during testing

---

## Phase 1: The Archivist — Capture Pipeline

### 1.1 Content Input Edge Cases

#### Edge Case 1.1.1: Empty Content
**Description**: User attempts to capture empty string or whitespace-only content
**Impact**: Invalid capture created, potential index corruption
**Detection**: `len(content.strip()) == 0`
**Mitigation**: 
- Raise `ValueError` with descriptive message
- Validate before UUID generation
- Log attempt for monitoring
**Priority**: High
**Component**: `capture_note()`

#### Edge Case 1.1.2: Extremely Long Content
**Description**: Note content exceeds reasonable limits (e.g., >1MB text)
**Impact**: Filesystem bloat, slow processing, memory issues
**Detection**: `len(content) > MAX_CONTENT_LENGTH` (configurable)
**Mitigation**:
- Truncate with warning
- Reject with error message
- Suggest file capture instead
**Priority**: Medium
**Component**: `capture_note()`

#### Edge Case 1.1.3: Special Characters and Unicode
**Description**: Content contains emojis, special unicode, or control characters
**Impact**: JSON encoding errors, display issues
**Detection**: Try-except during JSON serialization
**Mitigation**:
- Use `ensure_ascii=False` in JSON encoding
- Sanitize control characters
- Test with various unicode samples
**Priority**: Medium
**Component**: `capture_note()`

#### Edge Case 1.1.4: Malformed Content
**Description**: Content contains invalid UTF-8 sequences or binary data
**Impact**: Encoding errors, data corruption
**Detection**: Unicode decode errors during processing
**Mitigation**:
- Detect encoding automatically
- Fall back to latin-1 or binary mode
- Store as base64 if necessary
**Priority**: High
**Component**: `capture_note()`

### 1.2 URL Capture Edge Cases

#### Edge Case 1.2.1: Invalid URL Format
**Description**: URL doesn't match standard format (e.g., "not-a-url")
**Impact**: Validation failure, user confusion
**Detection**: URL parsing library validation
**Mitigation**:
- Use robust URL validator (e.g., `validators` library)
- Provide helpful error message
- Suggest correct format
**Priority**: High
**Component**: `capture_link()`

#### Edge Case 1.2.2: Unreachable URL
**Description**: URL is valid but server is down or network unavailable
**Impact**: Capture failure, timeout
**Detection**: Network timeout, connection error
**Mitigation**:
- Implement timeout (e.g., 10 seconds)
- Store URL anyway with "unreachable" status
- Allow retry later
- Add user notification
**Priority**: Medium
**Component**: `capture_link()`

#### Edge Case 1.2.3: Redirect Loops
**Description**: URL redirects infinitely between pages
**Impact**: Infinite loop, resource exhaustion
**Detection**: Redirect count > MAX_REDIRECTS (e.g., 10)
**Mitigation**:
- Limit redirect count
- Store final URL after redirects
- Log redirect chain for debugging
**Priority**: Medium
**Component**: `capture_link()`

#### Edge Case 1.2.4: Large Page Content
**Description**: URL points to very large page (e.g., 10MB+)
**Impact**: Memory exhaustion, slow processing
**Detection**: Content-Length header or size after fetch
**Mitigation**:
- Limit content size (e.g., 1MB)
- Store only metadata if too large
- Warn user about size limit
**Priority**: Medium
**Component**: `capture_link()`

#### Edge Case 1.2.5: Blocked by Robots.txt or CAPTCHA
**Description**: URL blocks automated access
**Impact**: Fetch failure, incomplete capture
**Detection**: HTTP 403, CAPTCHA detection
**Mitigation**:
- Respect robots.txt
- Store URL with "blocked" status
- Allow manual content entry
**Priority**: Low
**Component**: `capture_link()`

#### Edge Case 1.2.6: Non-HTML Content
**Description**: URL points to PDF, video, or other non-text content
**Impact**: Content extraction failure
**Detection**: Content-Type header
**Mitigation**:
- Store content-type in metadata
- Attempt text extraction if possible
- Store as file reference
**Priority**: Medium
**Component**: `capture_link()`

### 1.3 File Capture Edge Cases

#### Edge Case 1.3.1: Non-Existent File
**Description**: File path doesn't exist
**Impact**: FileNotFoundError, capture failure
**Detection**: `os.path.exists()` check
**Mitigation**:
- Raise clear error message
- Suggest valid path
- Allow retry with different path
**Priority**: High
**Component**: `capture_file()`

#### Edge Case 1.3.2: Permission Denied
**Description**: File exists but no read permissions
**Impact**: PermissionError, capture failure
**Detection**: Try-except on file open
**Mitigation**:
- Check file permissions before read
- Provide clear error message
- Suggest permission fix
**Priority**: High
**Component**: `capture_file()`

#### Edge Case 1.3.3: Binary File
**Description**: File is binary (e.g., .exe, .png)
**Impact**: Text extraction failure, encoding errors
**Detection**: File extension, binary content detection
**Mitigation**:
- Store as file reference only
- Extract metadata (size, type)
- Don't attempt content extraction
**Priority**: Medium
**Component**: `capture_file()`

#### Edge Case 1.3.4: Very Large File
**Description**: File size exceeds limits (e.g., >100MB)
**Impact**: Memory exhaustion, slow processing
**Detection**: File size check
**Mitigation**:
- Reject with size limit error
- Suggest splitting or compression
- Store metadata only
**Priority**: Medium
**Component**: `capture_file()`

#### Edge Case 1.3.5: Corrupted File
**Description**: File is corrupted or partially written
**Impact**: Read errors, data corruption
**Detection**: Read errors, encoding errors
**Mitigation**:
- Detect corruption during read
- Store error status
- Allow partial capture if possible
**Priority**: Low
**Component**: `capture_file()`

#### Edge Case 1.3.6: Locked File
**Description**: File is locked by another process
**Impact**: PermissionError, capture failure
**Detection**: File open error
**Mitigation**:
- Retry with delay
- Provide clear error message
- Suggest closing file
**Priority**: Medium
**Component**: `capture_file()`

### 1.4 Filesystem Edge Cases

#### Edge Case 1.4.1: Disk Full
**Description**: No disk space available for new capture
**Impact**: Write failure, data loss
**Detection**: OSError during write
**Mitigation**:
- Check available space before write
- Provide clear error message
- Suggest cleanup
**Priority**: High
**Component**: All capture functions

#### Edge Case 1.4.2: Directory Not Writable
**Description**: `raw/` directory lacks write permissions
**Impact**: Write failure, capture pipeline broken
**Detection**: Permission error on directory write
**Mitigation**:
- Check directory permissions on startup
- Create directory if missing
- Provide setup instructions
**Priority**: High
**Component**: All capture functions

#### Edge Case 1.4.3: Index File Corruption
**Description**: `raw/index.json` is corrupted or malformed
**Impact**: Index deserialization failure, duplicate UUIDs
**Detection**: JSON decode error
**Mitigation**:
- Validate index on load
- Backup index before updates
- Rebuild index from raw files if corrupted
- Use atomic writes (write to temp, then rename)
**Priority**: High
**Component**: Index management

#### Edge Case 1.4.4: Concurrent Access
**Description**: Multiple processes writing to index simultaneously
**Impact**: Race conditions, data corruption
**Detection**: File locking issues, inconsistent state
**Mitigation**:
- Use file locking (fcntl or portalocker)
- Implement retry logic
- Use atomic writes
- Consider database for production
**Priority**: Medium
**Component**: Index management

#### Edge Case 1.4.5: UUID Collision
**Description**: Extremely rare case of duplicate UUID generation
**Impact**: Data overwriting, loss
**Detection**: Check if UUID exists before write
**Mitigation**:
- Check for existing UUID
- Regenerate if collision
- Log collision for monitoring
**Priority**: Low
**Component**: UUID generation

### 1.5 Index Management Edge Cases

#### Edge Case 1.5.1: Empty Index
**Description**: Index file doesn't exist or is empty
**Impact**: First capture, index initialization
**Detection**: File not found or empty read
**Mitigation**:
- Initialize empty index structure
- Create file if missing
- Handle gracefully
**Priority**: Low
**Component**: Index management

#### Edge Case 1.5.2: Orphaned Files
**Description**: Raw files exist but not in index
**Impact**: Data inconsistency, lost captures
**Detection**: Compare directory listing with index
**Mitigation**:
- Implement recovery function
- Add orphaned files to index
- Log for review
**Priority**: Medium
**Component**: Index management

#### Edge Case 1.5.3: Stale Index Entries
**Description**: Index references files that don't exist
**Impact**: Broken references, errors
**Detection**: Check file existence for each index entry
**Mitigation**:
- Remove stale entries
- Log cleanup
- Implement consistency check
**Priority**: Medium
**Component**: Index management

---

## Phase 2: The Librarian — Classification and Linking

### 2.1 LLM API Edge Cases

#### Edge Case 2.1.1: API Rate Limits
**Description**: Groq API rate limit exceeded
**Impact**: Classification failure, batch processing stops
**Detection**: HTTP 429 response
**Mitigation**:
- Implement exponential backoff
- Queue requests for retry
- Rate limit outgoing requests
- Provide user feedback
**Priority**: High
**Component**: `llm_client.py`

#### Edge Case 2.1.2: API Key Invalid/Expired
**Description**: API key is invalid or has expired
**Impact**: All API calls fail
**Detection**: HTTP 401/403 response
**Mitigation**:
- Validate API key on startup
- Provide clear error message
- Suggest key renewal
- Add key rotation support
**Priority**: High
**Component**: `llm_client.py`

#### Edge Case 2.1.3: API Downtime
**Description**: Groq API is temporarily unavailable
**Impact**: Classification pipeline stops
**Detection**: Connection timeout, HTTP 5xx
**Mitigation**:
- Implement retry with exponential backoff
- Queue failed classifications
- Provide fallback to local model
- Notify user of service issues
**Priority**: High
**Component**: `llm_client.py`

#### Edge Case 2.1.4: API Timeout
**Description**: API call takes too long to respond
**Impact**: Classification timeout, user frustration
**Detection**: Request timeout (e.g., 30 seconds)
**Mitigation**:
- Set reasonable timeout
- Retry with longer timeout
- Queue for later processing
- Log timeout for monitoring
**Priority**: Medium
**Component**: `llm_client.py`

#### Edge Case 2.1.5: Malformed API Response
**Description**: API returns non-JSON or unexpected structure
**Impact**: Parsing failure, classification lost
**Detection**: JSON decode error, schema validation
**Mitigation**:
- Validate response structure
- Log malformed responses
- Retry request
- Fall back to default classification
**Priority**: High
**Component**: `llm_client.py`

#### Edge Case 2.1.6: API Response Too Large
**Description**: API response exceeds expected size
**Impact**: Memory issues, slow processing
**Detection**: Response size > MAX_RESPONSE_SIZE
**Mitigation**:
- Limit response size
- Truncate if necessary
- Log oversized responses
**Priority**: Low
**Component**: `llm_client.py`

### 2.2 Classification Edge Cases

#### Edge Case 2.2.1: Empty Content for Classification
**Description**: Raw capture has empty or whitespace-only content
**Impact**: LLM receives no input, meaningless classification
**Detection**: Content length check
**Mitigation**:
- Skip classification with warning
- Assign default category (e.g., "Archives")
- Log for review
**Priority**: Medium
**Component**: `classify_capture()`

#### Edge Case 2.2.2: Content Exceeds Context Window
**Description**: Content is too long for LLM context window
**Impact**: Truncated input, poor classification
**Detection**: Content length > MAX_CONTEXT_LENGTH
**Mitigation**:
- Truncate intelligently (keep beginning/end)
- Summarize before classification
- Chunk and classify separately
- Log truncation
**Priority**: High
**Component**: `classify_capture()`

#### Edge Case 2.2.3: Ambiguous Content
**Description**: Content is too vague for clear PARA classification
**Impact**: Inconsistent or random classification
**Detection**: Low confidence score from LLM
**Mitigation**:
- Use confidence threshold
- Assign to "Resources" as default
- Flag for manual review
- Improve prompt with examples
**Priority**: Medium
**Component**: `classify_capture()`

#### Edge Case 2.2.4: Non-English Content
**Description**: Content is in non-English language
**Impact**: LLM may misclassify or fail
**Detection**: Language detection
**Mitigation**:
- Detect language before classification
- Use multilingual model if available
- Add language to metadata
- Flag for manual review
**Priority**: Medium
**Component**: `classify_capture()`

#### Edge Case 2.2.5: Code or Technical Content
**Description**: Content is code snippets or technical documentation
**Impact**: Misclassification, poor tagging
**Detection**: Pattern matching for code
**Mitigation**:
- Add code-specific examples to prompt
- Detect code blocks
- Assign to "Resources" by default
**Priority**: Low
**Component**: `classify_capture()`

#### Edge Case 2.2.6: Invalid PARA Category in Response
**Description**: LLM returns category not in PARA framework
**Impact**: Invalid wiki note, validation failure
**Detection**: Category validation against allowed values
**Mitigation**:
- Validate category before saving
- Map to closest valid category
- Default to "Resources"
- Log invalid categories
**Priority**: High
**Component**: `classify_capture()`

#### Edge Case 2.2.7: Missing Required Fields in Response
**Description**: LLM response missing category, tags, or summary
**Impact**: Incomplete classification, wiki note creation failure
**Detection**: Schema validation
**Mitigation**:
- Validate response structure
- Retry request if incomplete
- Use default values for missing fields
- Log incomplete responses
**Priority**: High
**Component**: `classify_capture()`

#### Edge Case 2.2.8: Too Many Tags
**Description**: LLM returns excessive tags (e.g., 50+)
**Impact**: Cluttered wiki, performance issues
**Detection**: Tag count > MAX_TAGS (e.g., 20)
**Mitigation**:
- Limit to top N tags by confidence
- Remove duplicate tags
- Log tag count
**Priority**: Low
**Component**: `classify_capture()`

### 2.3 Batch Processing Edge Cases

#### Edge Case 2.3.1: Empty Batch
**Description**: Batch classification called with empty list
**Impact**: No-op, potential confusion
**Detection**: Empty list check
**Mitigation**:
- Return empty result with warning
- Log empty batch
- Validate input
**Priority**: Low
**Component**: `batch_classify()`

#### Edge Case 2.3.2: Partial Batch Failure
**Description**: Some items in batch fail, others succeed
**Impact**: Inconsistent state, data loss
**Detection**: Track success/failure per item
**Mitigation**:
- Continue processing on individual failures
- Save intermediate results
- Provide detailed error report
- Allow retry of failed items
**Priority**: High
**Component**: `batch_classify()`

#### Edge Case 2.3.3: Batch Interruption
**Description**: Batch processing interrupted (user cancel, system crash)
**Impact**: Partial processing, inconsistent state
**Detection**: Checkpoint file, progress tracking
**Mitigation**:
- Save progress after each item
- Implement resume capability
- Use checkpoint file
- Allow resume from interruption
**Priority**: High
**Component**: `batch_classify()`

#### Edge Case 2.3.4: Duplicate Items in Batch
**Description**: Same raw_id appears multiple times in batch
**Impact**: Duplicate processing, wasted API calls
**Detection**: Deduplicate input list
**Mitigation**:
- Deduplicate before processing
- Log duplicates
- Skip already processed items
**Priority**: Medium
**Component**: `batch_classify()`

### 2.4 Embedding Computation Edge Cases

#### Edge Case 2.4.1: Model Download Failure
**Description**: sentence-transformers model fails to download
**Impact**: Embedding computation impossible
**Detection**: Download error, model not found
**Mitigation**:
- Implement retry logic
- Use cached model if available
- Provide clear error message
- Fallback to different model
**Priority**: High
**Component**: `embeddings.py`

#### Edge Case 2.4.2: Model Load Failure
**Description**: Model file corrupted or incompatible
**Impact**: Embedding computation fails
**Detection**: Load error, version mismatch
**Mitigation**:
- Redownload model
- Validate model integrity
- Use version pinning
- Log model errors
**Priority**: High
**Component**: `embeddings.py`

#### Edge Case 2.4.3: Empty Text for Embedding
**Description**: Attempt to embed empty string
**Impact**: Model error, meaningless embedding
**Detection**: Empty string check
**Mitigation**:
- Skip embedding with warning
- Use zero vector or default
- Log for review
**Priority**: Medium
**Component**: `compute_embedding()`

#### Edge Case 2.4.4: Text Too Long for Model
**Description**: Text exceeds model's maximum token limit
**Impact**: Truncation, poor embedding quality
**Detection**: Token count check
**Mitigation**:
- Truncate intelligently
- Chunk and average embeddings
- Log truncation
**Priority**: Medium
**Component**: `compute_embedding()`

#### Edge Case 2.4.5: Embedding Dimension Mismatch
**Description**: Different models produce different dimensions
**Impact**: Similarity computation fails
**Detection**: Dimension check
**Mitigation**:
- Use consistent model
- Validate dimensions
- Re-compute if mismatch
- Log dimension issues
**Priority**: High
**Component**: `compute_embedding()`

#### Edge Case 2.4.6: Out of Memory During Embedding
**Description**: Large batch or model causes OOM
**Impact**: Process crash, data loss
**Detection**: MemoryError
**Mitigation**:
- Process in smaller batches
- Clear cache between batches
- Use model quantization
- Monitor memory usage
**Priority**: Medium
**Component**: `compute_embedding()`

### 2.5 Embedding Cache Edge Cases

#### Edge Case 2.5.1: Cache Directory Missing
**Description**: `wiki/embeddings/` directory doesn't exist
**Impact**: Cache lookup fails
**Detection**: Directory existence check
**Mitigation**:
- Create directory on demand
- Handle missing cache gracefully
- Log directory creation
**Priority**: Low
**Component**: Cache management

#### Edge Case 2.5.2: Corrupted Cache File
**Description**: `.npy` file is corrupted
**Impact**: Cache load failure, recomputation needed
**Detection**: Load error, file validation
**Mitigation**:
- Detect corruption on load
- Delete corrupted file
- Recompute embedding
- Log corruption
**Priority**: Medium
**Component**: Cache management

#### Edge Case 2.5.3: Cache File Missing for Wiki Note
**Description**: Wiki note references embedding that doesn't exist
**Impact**: Linking failure, broken reference
**Detection**: File existence check
**Mitigation**:
- Recompute missing embedding
- Update wiki note reference
- Log missing cache
**Priority**: Medium
**Component**: Cache management

#### Edge Case 2.5.4: Cache Invalidation Race Condition
**Description**: Cache invalidated while being read
**Impact**: Stale data, computation errors
**Detection**: File modification time check
**Mitigation**:
- Use atomic operations
- Lock cache files during write
- Implement versioning
**Priority**: Low
**Component**: Cache management

#### Edge Case 2.5.5: Disk Full for Cache
**Description**: No space for new cache files
**Impact**: Caching fails, performance degradation
**Detection**: Disk space check
**Mitigation**:
- Check available space
- Clean old cache if needed
- Fall back to recomputation
- Warn user
**Priority**: Medium
**Component**: Cache management

### 2.6 Similarity Computation Edge Cases

#### Edge Case 2.6.1: Zero Vector Embedding
**Description**: Embedding is all zeros (error case)
**Impact**: Similarity computation meaningless
**Detection**: Vector norm check
**Mitigation**:
- Detect zero vectors
- Recompute embedding
- Use default similarity
- Log zero vectors
**Priority**: High
**Component**: `compute_similarity()`

#### Edge Case 2.6.2: NaN or Inf in Embedding
**Description**: Embedding contains NaN or Inf values
**Impact**: Similarity computation fails
**Detection**: Value check
**Mitigation**:
- Detect invalid values
- Recompute embedding
- Clean invalid values
- Log numerical errors
**Priority**: High
**Component**: `compute_similarity()`

#### Edge Case 2.6.3: Different Embedding Dimensions
**Description**: Comparing embeddings of different sizes
**Impact**: Computation error
**Detection**: Shape check
**Mitigation**:
- Validate dimensions before computation
- Pad or truncate if necessary
- Recompute with consistent model
- Log dimension mismatches
**Priority**: High
**Component**: `compute_similarity()`

#### Edge Case 2.6.4: Similarity Score Out of Range
**Description**: Similarity not in [0, 1] range
**Impact**: Threshold filtering fails
**Detection**: Range check
**Mitigation**:
- Clamp to [0, 1] range
- Investigate computation error
- Log out-of-range values
**Priority**: Medium
**Component**: `compute_similarity()`

#### Edge Case 2.6.5: All Similarities Below Threshold
**Description**: No notes meet similarity threshold
**Impact**: No links created, isolated note
**Detection**: Empty result list
**Mitigation**:
- Lower threshold adaptively
- Create no links (acceptable)
- Log low similarity case
- Suggest manual linking
**Priority**: Low
**Component**: `find_related_notes()`

#### Edge Case 2.6.6: All Similarities Above Threshold
**Description**: Too many notes meet threshold (e.g., >100)
**Impact**: Over-linking, performance issues
**Detection**: Result count > MAX_LINKS (e.g., 50)
**Mitigation**:
- Limit to top N by similarity
- Increase threshold adaptively
- Log over-linking
**Priority**: Medium
**Component**: `find_related_notes()`

### 2.7 Auto-Linking Edge Cases

#### Edge Case 2.7.1: Empty Wiki
**Description**: First note being linked, no existing notes
**Impact**: No links created (expected)
**Detection**: Empty wiki check
**Mitigation**:
- Handle gracefully (no-op)
- Log first note
- Proceed without links
**Priority**: Low
**Component**: `auto_link()`

#### Edge Case 2.7.2: Self-Linking
**Description**: Note linked to itself
**Impact**: Confusing graph, meaningless link
**Detection**: UUID comparison
**Mitigation**:
- Exclude self from similarity search
- Filter self-links
- Log self-link attempts
**Priority**: Medium
**Component**: `auto_link()`

#### Edge Case 2.7.3: Duplicate Links
**Description**: Same link created multiple times
**Impact**: Redundant edges, cluttered graph
**Detection**: Link existence check
**Mitigation**:
- Check existing links before adding
- Use set for link storage
- Deduplicate links
**Priority**: Medium
**Component**: `auto_link()`

#### Edge Case 2.7.4: Reciprocal Link Conflict
**Description**: Reciprocal link already exists with different similarity
**Impact**: Inconsistent edge weights
**Detection**: Link existence check
**Mitigation**:
- Update similarity to max of both
- Keep most recent
- Log conflict
**Priority**: Low
**Component**: `auto_link()`

#### Edge Case 2.7.5: Circular Linking
**Description**: A links to B, B links to C, C links to A
**Impact**: Clusters, not necessarily bad
**Detection**: Graph cycle detection
**Mitigation**:
- Allow cycles (semantic clusters)
- Detect for monitoring
- Log large cycles
**Priority**: Low
**Component**: `auto_link()`

#### Edge Case 2.7.6: Link to Deleted Note
**Description**: Link references note that was deleted
**Impact**: Broken reference, graph error
**Detection**: Note existence check
**Mitigation**:
- Validate target note exists
- Remove broken links
- Implement cleanup
**Priority**: High
**Component**: `auto_link()`

### 2.8 Wiki Creation Edge Cases

#### Edge Case 2.8.1: Raw Capture Not Found
**Description**: Raw capture ID doesn't exist
**Impact**: Wiki creation failure
**Detection**: File existence check
**Mitigation**:
- Raise clear error
- Log missing capture
- Suggest re-capture
**Priority**: High
**Component**: `create_wiki_note()`

#### Edge Case 2.8.2: Classification Missing
**Description**: Classification data not provided
**Impact**: Incomplete wiki note
**Detection**: None check for classification
**Mitigation**:
- Require classification
- Use defaults if missing
- Log missing data
**Priority**: High
**Component**: `create_wiki_note()`

#### Edge Case 2.8.3: Duplicate Wiki Note
**Description**: Wiki note with same ID already exists
**Impact**: Data overwriting
**Detection**: File existence check
**Mitigation**:
- Check before write
- Generate new UUID if conflict
- Log duplicate attempt
**Priority**: High
**Component**: `create_wiki_note()`

#### Edge Case 2.8.4: Wiki Index Corruption
**Description**: Wiki index file corrupted
**Impact**: Index operations fail
**Detection**: JSON decode error
**Mitigation**:
- Validate index on load
- Rebuild from wiki files
- Use atomic writes
- Backup index
**Priority**: High
**Component**: Wiki index management

---

## Phase 3: The Cartographer — Graph Visualization

### 3.1 Graph Building Edge Cases

#### Edge Case 3.1.1: Empty Wiki
**Description**: No wiki notes exist
**Impact**: Empty graph, nothing to visualize
**Detection**: Empty wiki directory
**Mitigation**:
- Display empty state message
- Show helpful instructions
- Handle gracefully
**Priority**: Low
**Component**: `build_graph.py`

#### Edge Case 3.1.2: Single Node
**Description**: Only one wiki note exists
**Impact**: Single node, no edges
**Detection**: Node count == 1
**Mitigation**:
- Display single node
- Show helpful message
- Handle gracefully
**Priority**: Low
**Component**: `build_graph.py`

#### Edge Case 3.1.3: Disconnected Components
**Description**: Multiple unconnected clusters
**Impact**: Fragmented graph
**Detection**: Graph connectivity analysis
**Mitigation**:
- Display all components
- Allow filtering by component
- Log disconnected components
**Priority**: Low
**Component**: `build_graph.py`

#### Edge Case 3.1.4: Missing Node Attributes
**Description**: Wiki note missing required attributes
**Impact**: Incomplete node data
**Detection**: Attribute validation
**Mitigation**:
- Use default values
- Log missing attributes
- Validate before export
**Priority**: Medium
**Component**: `build_nodes()`

#### Edge Case 3.1.5: Invalid Edge References
**Description**: Edge references non-existent node
**Impact**: Broken graph, rendering error
**Detection**: Node existence check
**Mitigation**:
- Validate edge targets
- Remove invalid edges
- Log broken references
**Priority**: High
**Component**: `build_edges()`

#### Edge Case 3.1.6: Duplicate Edges
**Description**: Same edge appears multiple times
**Impact**: Redundant edges
**Detection**: Edge deduplication
**Mitigation**:
- Remove duplicates
- Keep highest weight
- Log duplicates
**Priority**: Medium
**Component**: `build_edges()`

#### Edge Case 3.1.7: Self-Loops
**Description**: Edge from node to itself
**Impact**: Confusing visualization
**Detection**: From == To check
**Mitigation**:
- Remove self-loops
- Log occurrences
**Priority**: Medium
**Component**: `build_edges()`

#### Edge Case 3.1.8: Very Large Graph
**Description**: Thousands of nodes and edges
**Impact**: Rendering performance issues
**Detection**: Node/edge count threshold
**Mitigation**:
- Implement pagination
- Limit initial render
- Use lazy loading
- Warn user
**Priority**: High
**Component**: `build_graph.py`

#### Edge Case 3.1.9: Dense Graph
**Description**: High edge-to-node ratio (almost complete graph)
**Impact**: Visual clutter, performance issues
**Detection**: Edge density > threshold
**Mitigation**:
- Filter by edge weight
- Limit edges per node
- Use minimum spanning tree
**Priority**: Medium
**Component**: `build_edges()`

#### Edge Case 3.1.10: Graph JSON Export Failure
**Description**: JSON write fails (disk full, permissions)
**Impact**: Graph not saved
**Detection**: Write error
**Mitigation**:
- Check disk space
- Validate permissions
- Use atomic write
- Retry with temp location
**Priority**: High
**Component**: `export_graph()`

### 3.2 Graph Visualization Edge Cases

#### Edge Case 3.2.1: WebGL Not Supported
**Description**: Browser doesn't support WebGL
**Impact**: Graph doesn't render
**Detection**: WebGL capability check
**Mitigation**:
- Fallback to canvas rendering
- Show error message
- Suggest browser upgrade
**Priority**: Medium
**Component**: Graph rendering

#### Edge Case 3.2.2: JavaScript Errors
**Description**: JS errors in graph library
**Impact**: Graph doesn't render or interact
**Detection**: Try-catch in JS
**Mitigation**:
- Catch and log errors
- Show error message
- Provide fallback
**Priority**: High
**Component**: Graph rendering

#### Edge Case 3.2.3: Mobile Rendering Issues
**Description**: Graph doesn't render well on mobile
**Impact**: Poor mobile UX
**Detection**: User agent detection
**Mitigation**:
- Responsive design
- Touch-friendly controls
- Simplified mobile view
**Priority**: Medium
**Component**: Graph rendering

#### Edge Case 3.2.4: Dark Mode Contrast Issues
**Description**: Poor contrast in dark mode
**Impact**: Unreadable graph
**Detection**: Color contrast analysis
**Mitigation**:
- Test color schemes
- Adjust colors for dark mode
- Provide theme toggle
**Priority**: Medium
**Component**: Graph styling

#### Edge Case 3.2.5: Tooltip Overflow
**Description**: Tooltip content too large for screen
**Impact**: UI clutter, unreadable
**Detection**: Content size check
**Mitigation**:
- Truncate tooltip content
- Add scroll to tooltip
- Limit preview length
**Priority**: Low
**Component**: Graph interaction

#### Edge Case 3.2.6: Zoom/Pan Extremes
**Description**: User zooms too far in or out
**Impact**: Lost context or unreadable
**Detection**: Zoom level check
**Mitigation**:
- Clamp zoom levels
- Provide reset button
- Limit pan bounds
**Priority**: Low
**Component**: Graph interaction

#### Edge Case 3.2.7: Node Drag Failure
**Description**: Drag and drop doesn't work
**Impact**: Poor UX
**Detection**: Event handler check
**Mitigation**:
- Test drag handlers
- Fallback to click selection
- Log failures
**Priority**: Medium
**Component**: Graph interaction

#### Edge Case 3.2.8: Performance Degradation
**Description**: Graph becomes slow with many nodes
**Impact**: Poor UX, browser freeze
**Detection**: Frame rate monitoring
**Mitigation**:
- Implement level-of-detail
- Use WebGL acceleration
- Limit visible nodes
- Optimize rendering
**Priority**: High
**Component**: Graph rendering

#### Edge Case 3.2.9: Filter State Inconsistency
**Description**: Filter state doesn't match graph
**Impact**: Confusing UX
**Detection**: State validation
**Mitigation**:
- Sync filter state
- Reset filters on graph update
- Validate before apply
**Priority**: Medium
**Component**: Graph filtering

#### Edge Case 3.2.10: Graph Auto-Update Failure
**Description**: Graph doesn't update after new note
**Impact**: Stale visualization
**Detection**: Change detection
**Mitigation**:
- Implement watch mechanism
- Force refresh on capture
- Log update failures
**Priority**: High
**Component**: Graph auto-update

### 3.3 Node/Edge Attribute Edge Cases

#### Edge Case 3.3.1: Missing Category
**Description**: Note has no PARA category
**Impact**: Color assignment fails
**Detection**: Category validation
**Mitigation**:
- Use default color
- Assign to "Resources"
- Log missing category
**Priority**: Medium
**Component**: Node building

#### Edge Case 3.3.2: Invalid Category
**Description**: Category not in PARA framework
**Impact**: Color assignment fails
**Detection**: Category validation
**Mitigation**:
- Map to valid category
- Use default color
- Log invalid category
**Priority**: Medium
**Component**: Node building

#### Edge Case 3.3.3: Empty Summary
**Description**: Note has no summary
**Impact**: Label generation fails
**Detection**: Summary validation
**Mitigation**:
- Use content preview
- Use "Untitled" as default
- Truncate content for label
**Priority**: Low
**Component**: Node building

#### Edge Case 3.3.4: Very Long Label
**Description**: Label too long for display
**Impact**: Visual clutter
**Detection**: Label length check
**Mitigation**:
- Truncate label
- Use ellipsis
- Show full on hover
**Priority**: Low
**Component**: Node building

#### Edge Case 3.3.5: Zero Link Count
**Description**: Node has no links
**Impact**: Size calculation (zero size)
**Detection**: Link count check
**Mitigation**:
- Use minimum size
- Add base size
- Log isolated nodes
**Priority**: Low
**Component**: Node building

#### Edge Case 3.3.6: Extreme Link Count
**Description**: Node has hundreds of links
**Impact**: Disproportionate size
**Detection**: Link count threshold
**Mitigation**:
- Cap maximum size
- Use logarithmic scaling
- Log hub nodes
**Priority**: Medium
**Component**: Node building

#### Edge Case 3.3.7: Invalid Edge Weight
**Description**: Edge weight not in expected range
**Impact**: Rendering issues
**Detection**: Weight validation
**Mitigation**:
- Clamp to valid range
- Use default weight
- Log invalid weights
**Priority**: Medium
**Component**: Edge building

#### Edge Case 3.3.8: Missing Edge Weight
**Description**: Edge has no weight
**Impact**: Rendering uses default
**Detection**: Weight existence check
**Mitigation**:
- Use default weight
- Log missing weights
**Priority**: Low
**Component**: Edge building

---

## Phase 4: The Oracle — Query and Deployment

### 4.1 RAG Query Edge Cases

#### Edge Case 4.1.1: Empty Question
**Description**: User submits empty question
**Impact**: Meaningless query, wasted API call
**Detection**: Empty string check
**Mitigation**:
- Reject with error message
- Require input
- Log empty queries
**Priority**: High
**Component**: `ask()`

#### Edge Case 4.1.2: Very Long Question
**Description**: Question exceeds reasonable length
**Impact**: Slow processing, token limit
**Detection**: Length check
**Mitigation**:
- Truncate with warning
- Suggest shorter question
- Log long queries
**Priority**: Medium
**Component**: `ask()`

#### Edge Case 4.1.3: Question Too Short
**Description**: Single word or very short question
**Impact**: Poor retrieval, vague results
**Detection**: Length check
**Mitigation**:
- Accept but warn
- Suggest more detail
- Log short queries
**Priority**: Low
**Component**: `ask()`

#### Edge Case 4.1.4: Non-English Question
**Description**: Question in non-English language
**Impact**: Embedding mismatch, poor retrieval
**Detection**: Language detection
**Mitigation**:
- Detect language
- Use multilingual model
- Warn about language mismatch
- Log non-English queries
**Priority**: Medium
**Component**: `ask()`

#### Edge Case 4.1.5: Question About Non-Existent Topic
**Description**: No relevant notes in wiki
**Impact**: No retrieval, poor answer
**Detection**: Empty retrieval result
**Mitigation**:
- Return "no information found"
- Suggest capturing relevant info
- Log topic gaps
**Priority**: Low
**Component**: `retrieve_relevant_notes()`

#### Edge Case 4.1.6: Ambiguous Question
**Description**: Question has multiple interpretations
**Impact**: Mixed retrieval, confusing answer
**Detection**: Low confidence in retrieval
**Mitigation**:
- Return multiple interpretations
- Ask for clarification
- Suggest rephrasing
**Priority**: Medium
**Component**: `retrieve_relevant_notes()`

#### Edge Case 4.1.7: Question Requires External Knowledge
**Description**: Answer not in personal knowledge
**Impact**: Hallucination, incorrect answer
**Detection**: Low retrieval scores
**Mitigation**:
- Refuse to answer
- Suggest capturing info
- Use web search (future feature)
- Log knowledge gaps
**Priority**: High
**Component**: `ask()`

#### Edge Case 4.1.8: Top-K Larger Than Available Notes
**Description**: User requests more notes than exist
**Impact**: Requested count not met
**Detection**: Available count check
**Mitigation**:
- Return all available notes
- Warn about limited results
- Log request
**Priority**: Low
**Component**: `retrieve_relevant_notes()`

#### Edge Case 4.1.9: Invalid Top-K Value
**Description**: Top-K is negative or zero
**Impact**: Invalid retrieval
**Detection**: Value validation
**Mitigation**:
- Use default value
- Warn user
- Log invalid values
**Priority**: Medium
**Component**: `retrieve_relevant_notes()`

### 4.2 Retrieval Edge Cases

#### Edge Case 4.2.1: Empty Wiki
**Description**: No notes to retrieve from
**Impact**: No retrieval possible
**Detection**: Empty wiki check
**Mitigation**:
- Return "no notes available"
- Suggest capturing info
- Handle gracefully
**Priority**: Low
**Component**: `retrieve_relevant_notes()`

#### Edge Case 2.2: All Embeddings Missing
**Description**: Wiki notes have no cached embeddings
**Impact**: Retrieval impossible
**Detection**: Embedding existence check
**Mitigation**:
- Recompute embeddings
- Fall back to keyword search
- Log missing embeddings
**Priority**: High
**Component**: `retrieve_relevant_notes()`

#### Edge Case 4.2.3: Some Embeddings Missing
**Description**: Partial embedding cache
**Impact**: Incomplete retrieval
**Detection**: Embedding existence check
**Mitigation**:
- Skip notes without embeddings
- Recompute missing embeddings
- Log partial cache
**Priority**: Medium
**Component**: `retrieve_relevant_notes()`

#### Edge Case 4.2.4: Embedding Dimension Mismatch
**Description**: Question embedding dimension differs from notes
**Impact**: Similarity computation fails
**Detection**: Dimension check
**Mitigation**:
- Recompute with consistent model
- Pad/truncate if necessary
- Log dimension mismatch
**Priority**: High
**Component**: `retrieve_relevant_notes()`

#### Edge Case 4.2.5: Low Similarity Scores
**Description**: All retrieved notes have low similarity
**Impact**: Poor answer quality
**Detection**: Similarity threshold check
**Mitigation**:
- Lower threshold adaptively
- Warn about low relevance
- Return "no relevant info"
**Priority**: Medium
**Component**: `retrieve_relevant_notes()`

#### Edge Case 4.2.6: Cache Poisoning
**Description**: Cached query results are stale
**Impact**: Outdated answers
**Detection**: Wiki modification time check
**Mitigation**:
- Invalidate cache on wiki update
- Use TTL for cache
- Log cache hits/misses
**Priority**: Medium
**Component**: `retrieve_relevant_notes()`

### 4.3 RAG Prompt Edge Cases

#### Edge Case 4.3.1: Context Too Long
**Description**: Retrieved notes exceed LLM context window
**Impact**: Truncated context, poor answer
**Detection**: Token count check
**Mitigation**:
- Limit notes in context
- Summarize notes
- Truncate intelligently
**Priority**: High
**Component**: `build_rag_prompt()`

#### Edge Case 4.3.2: Empty Context
**Description**: No notes retrieved for context
**Impact**: LLM has no information
**Detection**: Empty context check
**Mitigation**:
- Skip answer generation
- Return "no information found"
- Suggest capturing info
**Priority**: Medium
**Component**: `build_rag_prompt()`

#### Edge Case 4.3.3: Redundant Context
**Description**: Retrieved notes contain duplicate information
**Impact**: Wasted tokens, potential confusion
**Detection**: Similarity between notes
**Mitigation**:
- Deduplicate similar notes
- Summarize duplicates
- Log redundancy
**Priority**: Low
**Component**: `build_rag_prompt()`

#### Edge Case 4.3.4: Conflicting Context
**Description**: Retrieved notes have contradictory information
**Impact**: Confusing answer, hallucination
**Detection**: Manual review, confidence scores
**Mitigation**:
- Flag contradictions
- Present both sides
- Ask for clarification
**Priority**: Medium
**Component**: `build_rag_prompt()`

#### Edge Case 4.3.5: Citation Format Errors
**Description**: LLM doesn't follow citation format
**Impact**: Broken source links
**Detection**: Response parsing
**Mitigation**:
- Enforce citation format in prompt
- Parse and validate citations
- Fallback to note IDs
**Priority**: High
**Component**: `synthesize_answer()`

### 4.4 Answer Synthesis Edge Cases

#### Edge Case 4.4.1: LLM Refuses to Answer
**Description**: LLM refuses due to safety/policy
**Impact**: No answer provided
**Detection**: Refusal message in response
**Mitigation**:
- Detect refusal
- Return "unable to answer"
- Log refusal
- Try alternative prompt
**Priority**: Medium
**Component**: `synthesize_answer()`

#### Edge Case 4.4.2: LLM Hallucination
**Description**: LLM invents information not in context
**Impact**: Incorrect answer
**Detection**: Fact-check against context
**Mitigation**:
- Enforce "use only provided context"
- Detect hallucinations
- Warn about uncertainty
**Priority**: High
**Component**: `synthesize_answer()`

#### Edge Case 4.4.3: Answer Too Long
**Description**: LLM generates excessively long answer
**Impact**: Display issues, token waste
**Detection**: Length check
**Mitigation**:
- Truncate with warning
- Request concise answer
- Log long answers
**Priority**: Low
**Component**: `synthesize_answer()`

#### Edge Case 4.4.4: Answer Too Short
**Description**: LLM gives minimal answer
**Impact**: Unhelpful response
**Detection**: Length check
**Mitigation**:
- Request more detail
- Accept if adequate
- Log short answers
**Priority**: Low
**Component**: `synthesize_answer()`

#### Edge Case 4.4.5: Missing Citations
**Description**: LLM doesn't cite sources
**Impact**: No source attribution
**Detection**: Citation parsing
**Mitigation**:
- Enforce citations in prompt
- Add default citations
- Log missing citations
**Priority**: High
**Component**: `synthesize_answer()`

#### Edge Case 4.4.6: Invalid Citation References
**Description**: Citations reference non-existent notes
**Impact**: Broken source links
**Detection**: Note existence check
**Mitigation**:
- Validate citations
- Remove invalid references
- Log invalid citations
**Priority**: High
**Component**: `synthesize_answer()`

### 4.5 Streamlit App Edge Cases

#### Edge Case 4.5.1: Session State Corruption
**Description**: Streamlit session state becomes inconsistent
**Impact**: App behaves unexpectedly
**Detection**: State validation
**Mitigation**:
- Initialize state properly
- Validate state on load
- Reset on corruption
- Log state issues
**Priority**: High
**Component**: `app.py`

#### Edge Case 4.5.2: Concurrent User Sessions
**Description**: Multiple users accessing app simultaneously
**Impact**: State confusion, data mixing
**Detection**: Session isolation check
**Mitigation**:
- Use session-specific state
- Avoid global state
- Test concurrent access
**Priority**: High
**Component**: `app.py`

#### Edge Case 4.5.3: File Upload Failure
**Description**: File upload fails (size, type, network)
**Impact**: Capture failure
**Detection**: Upload error handling
**Mitigation**:
- Validate file before upload
- Provide clear error messages
- Retry mechanism
- Log upload failures
**Priority**: Medium
**Component**: File upload

#### Edge Case 4.5.4: Real-Time Update Race Condition
**Description**: Graph updates while user interacting
**Impact**: Jarring UX, state confusion
**Detection**: Update timing
**Mitigation**:
- Debounce updates
- Warn user before update
- Use optimistic updates
**Priority**: Medium
**Component**: Real-time updates

#### Edge Case 4.5.5: Memory Leak in Streamlit
**Description**: App memory grows over time
**Impact**: Performance degradation, crash
**Detection**: Memory monitoring
**Mitigation**:
- Clear cache periodically
- Avoid large objects in state
- Restart app periodically
- Log memory usage
**Priority**: High
**Component**: `app.py`

#### Edge Case 4.5.6: Browser Incompatibility
**Description**: App doesn't work in certain browsers
**Impact**: Some users can't use app
**Detection**: User agent detection
**Mitigation**:
- Test on major browsers
- Provide compatibility info
- Graceful degradation
**Priority**: Medium
**Component**: Frontend

#### Edge Case 4.5.7: Mobile Responsiveness Issues
**Description**: App layout breaks on mobile
**Impact**: Poor mobile UX
**Detection**: Responsive design testing
**Mitigation**:
- Use responsive layout
- Test on mobile devices
- Simplify mobile view
**Priority**: Medium
**Component**: Frontend

### 4.6 Deployment Edge Cases

#### Edge Case 4.6.1: Environment Variable Missing
**Description**: Required env var not set in deployment
**Impact**: App fails to start
**Detection**: Startup validation
**Mitigation**:
- Validate all env vars on startup
- Provide clear error messages
- Document required variables
- Use defaults where possible
**Priority**: High
**Component**: Deployment

#### Edge Case 4.6.2: Dependency Version Conflict
**Description**: Package versions conflict in deployment
**Impact**: App fails to install/run
**Detection**: Dependency resolution
**Mitigation**:
- Pin all versions
- Use virtual environment
- Test clean install
- Document dependencies
**Priority**: High
**Component**: Deployment

#### Edge Case 4.6.3: Deployment Platform Outage
**Description**: Streamlit Cloud/HF Spaces down
**Impact**: App unavailable
**Detection**: Health check
**Mitigation**:
- Monitor platform status
- Have backup deployment
- Communicate outages
- Auto-retry deployment
**Priority**: Medium
**Component**: Deployment

#### Edge Case 4.6.4: Resource Limits Exceeded
**Description**: App exceeds CPU/memory limits
**Impact**: App throttled or killed
**Detection**: Resource monitoring
**Mitigation**:
- Monitor resource usage
- Optimize performance
- Upgrade plan if needed
- Implement graceful degradation
**Priority**: High
**Component**: Deployment

#### Edge Case 4.6.5: Cold Start Delay
**Description**: First request takes long to respond
**Impact**: Poor user experience
**Detection**: Response time monitoring
**Mitigation**:
- Implement warm-up
- Cache models
- Optimize startup
- Show loading state
**Priority**: Medium
**Component**: Deployment

#### Edge Case 4.6.6: Data Persistence Issues
**Description**: Data doesn't persist across deployments
**Impact**: Data loss on redeploy
**Detection**: Data validation after deploy
**Mitigation**:
- Use persistent storage
- Backup data before deploy
- Document persistence strategy
- Test redeployment
**Priority**: High
**Component**: Deployment

#### Edge Case 4.6.7: GitHub Sync Issues
**Description**: Deployment fails to sync with GitHub
**Impact**: Stale code deployed
**Detection**: Sync status check
**Mitigation**:
- Monitor sync status
- Manual trigger if needed
- Check webhook configuration
- Log sync failures
**Priority**: Medium
**Component**: Deployment

#### Edge Case 4.6.8: SSL/HTTPS Issues
**Description**: Certificate or SSL errors
**Impact**: Security warnings, blocked access
**Detection**: SSL validation
**Mitigation**:
- Use platform's SSL
- Monitor certificate expiry
- Force HTTPS
- Log SSL errors
**Priority**: High
**Component**: Deployment

---

## Cross-Phase Edge Cases

### 5.1 Data Consistency Edge Cases

#### Edge Case 5.1.1: Raw-Wiki Orphan
**Description**: Raw capture exists but no corresponding wiki note
**Impact**: Incomplete processing
**Detection**: Compare raw and wiki indices
**Mitigation**:
- Identify orphans
- Offer to process
- Log for review
**Priority**: Medium
**Component**: Data consistency

#### Edge Case 5.1.2: Wiki-Raw Orphan
**Description**: Wiki note exists but raw capture missing
**Impact**: Can't re-process
**Detection**: Raw existence check
**Mitigation**:
- Flag for review
- Keep wiki note
- Log orphan
**Priority**: Low
**Component**: Data consistency

#### Edge Case 5.1.3: Graph-Wiki Orphan
**Description**: Graph references deleted wiki note
**Impact**: Broken graph
**Detection**: Note existence check
**Mitigation**:
- Rebuild graph
- Remove orphaned nodes
- Log inconsistency
**Priority**: High
**Component**: Data consistency

#### Edge Case 5.1.4: Index-Wiki Mismatch
**Description**: Wiki index doesn't match actual wiki files
**Impact**: Broken references
**Detection**: Compare index with directory
**Mitigation**:
- Rebuild index
- Validate consistency
- Log mismatches
**Priority**: High
**Component**: Data consistency

### 5.2 Performance Edge Cases

#### Edge Case 5.2.1: Database Lock Contention
**Description**: Multiple operations lock same resource
**Impact**: Slow performance, timeouts
**Detection**: Lock wait timeout
**Mitigation**:
- Use appropriate locking
- Optimize transaction scope
- Retry with backoff
- Consider database for scale
**Priority**: Medium
**Component**: Performance

#### Edge Case 5.2.2: Memory Fragmentation
**Description**: Memory becomes fragmented over time
**Impact**: OOM errors, performance degradation
**Detection**: Memory profiling
**Mitigation**:
- Restart periodically
- Optimize memory usage
- Use memory pools
- Monitor fragmentation
**Priority**: Low
**Component**: Performance

#### Edge Case 5.2.3: CPU Throttling
**Description**: CPU usage throttled by platform
**Impact**: Slow processing
**Detection**: CPU monitoring
**Mitigation**:
- Optimize CPU usage
- Use batch processing
- Upgrade plan if needed
- Implement caching
**Priority**: Medium
**Component**: Performance

### 5.3 Security Edge Cases

#### Edge Case 5.3.1: API Key Exposure
**Description**: API key leaked in logs or error messages
**Impact**: Security breach, API abuse
**Detection**: Log scanning
**Mitigation**:
- Never log API keys
- Use environment variables
- Rotate exposed keys
- Audit logs regularly
**Priority**: Critical
**Component**: Security

#### Edge Case 5.3.2: Injection Attacks
**Description**: Malicious content injected via capture
**Impact**: XSS, code execution
**Detection**: Input validation
**Mitigation**:
- Sanitize all inputs
- Escape output
- Use parameterized queries
- Log suspicious inputs
**Priority**: High
**Component**: Security

#### Edge Case 5.3.3: Path Traversal
**Description**: Malicious file paths access system files
**Impact**: Data theft, system compromise
**Detection**: Path validation
**Mitigation**:
- Validate file paths
- Use safe file operations
- Restrict to data directory
- Log path violations
**Priority**: High
**Component**: Security

#### Edge Case 5.3.4: Denial of Service
**Description**: Overwhelmed with requests/captures
**Impact**: System unresponsive
**Detection**: Rate monitoring
**Mitigation**:
- Implement rate limiting
- Queue requests
- Monitor load
- Scale resources
**Priority**: Medium
**Component**: Security

### 5.4 User Experience Edge Cases

#### Edge Case 5.4.1: Confusing Error Messages
**Description**: Error messages are technical or unclear
**Impact**: User frustration, support burden
**Detection**: User feedback
**Mitigation**:
- Use plain language
- Provide action items
- Link to documentation
- Test error messages
**Priority**: Medium
**Component**: UX

#### Edge Case 5.4.2: No Feedback on Long Operations
**Description**: Long operations show no progress
**Impact**: User thinks app is frozen
**Detection**: User feedback
**Mitigation**:
- Show progress indicators
- Provide time estimates
- Allow cancellation
- Log operation status
**Priority**: Medium
**Component**: UX

#### Edge Case 5.4.3: Undo/Redo Not Available
**Description**: User can't undo mistakes
**Impact**: Data loss, frustration
**Detection**: User feedback
**Mitigation**:
- Implement undo for critical ops
- Confirm destructive actions
- Provide backup/restore
- Log all changes
**Priority**: Low
**Component**: UX

#### Edge Case 5.4.4: No Onboarding/Help
**Description**: New users don't know how to use app
**Impact**: Poor adoption, support burden
**Detection**: User analytics
**Mitigation**:
- Add onboarding tour
- Provide help documentation
- Add tooltips
- Show example data
**Priority**: Medium
**Component**: UX

---

## Testing Strategy for Edge Cases

### 6.1 Unit Testing
- Test each edge case in isolation
- Use mock data for external dependencies
- Verify error handling and logging
- Test boundary conditions

### 6.2 Integration Testing
- Test edge cases across component boundaries
- Test failure propagation
- Test recovery mechanisms
- Test with real data where possible

### 6.3 Manual Testing
- Create edge case test suite
- Test with intentionally bad data
- Test with extreme values
- Test failure scenarios

### 6.4 Automated Testing
- Add edge cases to CI/CD pipeline
- Use property-based testing
- Fuzz testing for inputs
- Load testing for performance

---

## Edge Case Prioritization Matrix

| Priority | Description | Action Timeline |
|----------|-------------|-----------------|
| Critical | Security breaches, data loss | Immediate fix |
| High | Core functionality broken | Fix in current sprint |
| Medium | Degraded UX, partial failures | Fix in next sprint |
| Low | Nice-to-have, rare occurrences | Backlog |

---

## Maintenance

### Adding New Edge Cases
1. Discover during testing or production
2. Document in this file
3. Add to test suite
4. Implement mitigation
5. Update priority based on impact

### Review Schedule
- Review edge cases monthly
- Update based on user feedback
- Retire resolved edge cases
- Add newly discovered cases

### Metrics
- Track edge case occurrence frequency
- Monitor mitigation effectiveness
- Measure user impact
- Prioritize based on data

---

## Conclusion

This edge case document provides comprehensive coverage of exceptional conditions across all phases of the SecondSelf project. By anticipating and handling these edge cases, the system will be more robust, reliable, and user-friendly.

**Key Principles**:
- Fail gracefully with clear error messages
- Log all exceptional conditions for monitoring
- Provide recovery mechanisms where possible
- Validate all inputs and outputs
- Test edge cases regularly
- Prioritize based on user impact

**Next Steps**:
1. Implement mitigations for high-priority edge cases
2. Add edge case tests to CI/CD pipeline
3. Monitor for new edge cases in production
4. Update this document regularly
