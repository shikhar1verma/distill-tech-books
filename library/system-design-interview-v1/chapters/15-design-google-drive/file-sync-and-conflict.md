---
title: "File Sync and Conflict Resolution"
book: "System Design Interview"
chapter: 15
tags: [system-design, sync, conflict-resolution, long-polling, notification, file-storage]
related: [block-server, metadata-database, notification-service, storage-optimization]
---

## Summary

**File synchronization** keeps files consistent across multiple devices. Changes are propagated via a notification service (long polling) that tells remote clients to pull updated metadata and download new/changed blocks. When two users edit the same file simultaneously, a **conflict** arises. The resolution strategy is **first write wins**: the first-processed version is accepted, and the second user receives both copies to merge manually.

## How It Works

### Upload and Sync Flow

```mermaid
sequenceDiagram
    participant C1 as Client 1
    participant API as API Servers
    participant BS as Block Servers
    participant CS as Cloud Storage
    participant NS as Notification Service
    participant C2 as Client 2

    C1->>API: 1. Send file metadata (status: pending)
    C1->>BS: 2. Upload changed blocks
    BS->>CS: 3. Store blocks
    CS-->>API: 4. Upload complete callback
    API->>API: 5. Update metadata (status: uploaded)
    API->>NS: 6. Notify file changed
    NS->>C2: 7. Push notification
    C2->>API: 8. Fetch updated metadata
    C2->>BS: 9. Download new/changed blocks
    C2->>C2: 10. Reconstruct file
```

### Conflict Resolution

```mermaid
graph TD
    C1[Client 1 edits file] --> S1{Processed first?}
    C2[Client 2 edits file] --> S2{Processed first?}
    S1 --> |Yes| W1[Client 1 version accepted]
    S2 --> |No| CONFLICT[Sync Conflict]
    CONFLICT --> BOTH[Client 2 receives both versions]
    BOTH --> MERGE[User merges or picks one]
```

**Rules**:
- The first version to be processed by the server wins
- The later version triggers a conflict notification to that client
- The client with the conflict sees both copies and decides how to resolve

## When to Use

- Multi-device file sync (cloud storage, note-taking apps)
- Collaborative file systems where multiple users share files
- Any system where concurrent edits to the same resource are possible

## Trade-offs

| Advantage | Disadvantage |
|-----------|-------------|
| First-write-wins is simple to implement | Second user must manually resolve conflicts |
| Notification service keeps all clients in sync | Long-polling connections consume server resources |
| Block-level sync minimizes data transfer | Conflict resolution UX can confuse non-technical users |
| Offline queue ensures no updates are lost | Offline clients may accumulate many conflicts |

## Real-World Examples

- **Dropbox** uses first-write-wins with conflicted copies saved as separate files (e.g., "file (conflicted copy).txt")
- **Google Drive** detects conflicts and shows a resolution dialog for Google Docs; for binary files, it keeps both versions
- **Git** uses three-way merge for conflict resolution, requiring manual resolution of conflicting hunks
- **OneDrive** creates "conflicting changes" copies for offline edit conflicts

## Common Pitfalls

- **Silently overwriting the second user's changes**: Always preserve both versions and notify the user
- **Not handling offline conflicts**: Users who edit while offline can create many conflicts when they reconnect; queue all changes and resolve in order
- **Assuming conflicts are rare**: In shared team folders, conflicts happen regularly; the UX must make resolution easy
- **Blocking sync on conflict**: Conflicts should not prevent other files from syncing; handle them independently
- **Not showing conflict history**: Users need to see what changed and who changed it to make informed merge decisions

## See Also

- [[block-server]]
- [[metadata-database]]
- [[notification-service]]
- [[storage-optimization]]
