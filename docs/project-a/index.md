I am project A

```mermaid
graph TD
    A[Start] --> B{Failure?};
    B -->|Yes|
    C --> D[Debug];
    D --> B;
    B ---->|No| E[Success!];
```