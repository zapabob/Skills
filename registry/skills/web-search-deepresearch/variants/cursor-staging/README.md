# Web Search Deepresearch Skill

## Overview

The **Web Search Deepresearch** skill transforms basic web search into comprehensive deep research capabilities. Inspired by ClaudeCode Cowork's research methodologies, this skill integrates multiple search engines, conducts recursive information gathering, evaluates source credibility, and generates structured research reports with timelines, trend analysis, and actionable insights.

## Key Features

### 🔍 Multi-Source Integration
- **Google Search API** - Broad coverage and web presence
- **Bing Web Search** - Diverse perspectives and news focus
- **DuckDuckGo** - Privacy-focused alternative search
- **Google Scholar** - Academic and scientific research
- **ArXiv** - Cutting-edge scientific papers
- **PubMed** - Medical and health research
- **News Aggregators** - Real-time news and current events

### 🔄 Recursive Deep Analysis
- **Depth-First Exploration** - Follow promising leads recursively
- **Cross-Referencing** - Validate information across multiple sources
- **Contradiction Detection** - Identify and resolve conflicting information
- **Quality Thresholds** - Maintain minimum credibility standards

### 🎯 Information Quality Assessment
- **Source Credibility Scoring** - Domain authority and publication metrics
- **Content Quality Analysis** - Information density and factual accuracy
- **Temporal Relevance** - Recency weighting and time-based filtering
- **Bias Detection** - Identify potential source biases

### 📊 Structured Research Reports
- **Executive Summaries** - Key findings and implications
- **Detailed Analysis** - Comprehensive source evaluation
- **Timeline Construction** - Historical development tracking
- **Trend Forecasting** - Future projections and scenarios
- **Actionable Recommendations** - Practical insights and next steps

## Usage Examples

### Comprehensive Topic Research
```bash
# Research emerging AI technologies
python scripts/run_deep_research.py research-topic \
  --query "quantum computing applications in drug discovery 2026" \
  --depth comprehensive \
  --sources google_scholar arxiv pubmed \
  --timeline-analysis \
  --credibility-threshold 0.9 \
  --max-sources 50
```

### Claim Verification
```bash
# Verify controversial claims
python scripts/run_deep_research.py verify-claim \
  --claim "Social media increases depression rates by 300% in teenagers" \
  --fact-checking \
  --contradiction-analysis \
  --confidence-level high
```

### Trend Analysis
```bash
# Analyze technology adoption trends
python scripts/run_deep_research.py analyze-trends \
  --topic "autonomous vehicle adoption rates" \
  --timeframe "2020-2026" \
  --forecast-horizon 5 \
  --market-analysis \
  --survey-data
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Required packages (install via pip):
  ```bash
  pip install requests beautifulsoup4 aiohttp lxml fuzzywuzzy python-levenshtein
  ```

### Skill Installation
1. Copy this skill to your Cursor skills directory:
   ```bash
   cp -r web-search-deepresearch ~/.cursor/skills/
   ```

2. Ensure the skill is discoverable by Cursor's agent system

## Configuration Options

### Basic Configuration
```json
{
  "default_depth": "comprehensive",
  "default_sources": ["google", "bing", "scholar"],
  "credibility_threshold": 0.8,
  "max_sources": 30,
  "enable_caching": true,
  "cache_ttl_hours": 24
}
```

### Advanced Configuration
```json
{
  "research_strategies": {
    "academic": {
      "sources": ["scholar", "arxiv", "pubmed"],
      "credibility_threshold": 0.9,
      "max_depth": 5
    },
    "business": {
      "sources": ["google", "bing", "news"],
      "credibility_threshold": 0.7,
      "include_market_data": true
    },
    "technical": {
      "sources": ["stackoverflow", "github", "docs"],
      "credibility_threshold": 0.8,
      "include_code_examples": true
    }
  }
}
```

## Research Methodologies

### Quality Assurance Framework
1. **Source Credibility Evaluation**
   - Domain authority assessment
   - Publication history analysis
   - Fact-checking track record

2. **Content Quality Metrics**
   - Information density scoring
   - Citation analysis
   - Cross-reference validation

3. **Temporal Analysis**
   - Recency weighting
   - Historical trend analysis
   - Future projection modeling

### Contradiction Resolution
1. **Detection Algorithms**
   - Semantic similarity analysis
   - Claim clustering
   - Conflict identification

2. **Resolution Strategies**
   - Source credibility comparison
   - Evidence strength evaluation
   - Consensus building

3. **Uncertainty Quantification**
   - Confidence interval calculation
   - Alternative explanation analysis
   - Recommendation certainty scoring

## API Integration

### Search Provider APIs
- **Google Custom Search API** - Programmable web search
- **Bing Web Search API** - Microsoft-powered search
- **DuckDuckGo Instant Answer API** - Privacy-focused search
- **Google Scholar API** - Academic literature search
- **Semantic Scholar API** - AI-powered academic search

### Content Processing APIs
- **Readability API** - Content extraction and cleaning
- **Diffbot API** - Advanced web content analysis
- **Embedly API** - Rich content previews and metadata

## Performance Optimization

### Intelligent Caching
- **Query Result Caching** - Avoid redundant searches
- **Source Credibility Caching** - Persistent credibility scores
- **Content Analysis Caching** - Reuse processed content

### Parallel Processing
- **Concurrent API Calls** - Multiple search providers simultaneously
- **Batch Processing** - Efficient bulk content analysis
- **Load Balancing** - Distribute workload across resources

### Memory Management
- **Streaming Processing** - Handle large result sets efficiently
- **Incremental Analysis** - Process results as they arrive
- **Resource Pooling** - Reuse connections and parsers

## Enterprise Features

### Compliance and Governance
- **Audit Logging** - Complete research activity tracking
- **Access Control** - Role-based research permissions
- **Data Retention** - Configurable result storage policies

### Team Collaboration
- **Shared Research Sessions** - Multi-user collaborative research
- **Research Templates** - Standardized research methodologies
- **Knowledge Base Integration** - Persistent research result storage

### Advanced Analytics
- **Research Pattern Recognition** - Identify successful research strategies
- **Performance Metrics** - Track research effectiveness and efficiency
- **Continuous Improvement** - Learn from research outcomes

## Troubleshooting

### Common Issues

#### Low-Quality Results
**Symptoms:** Irrelevant or unreliable information
**Solutions:**
- Increase credibility threshold
- Add more authoritative sources
- Enable contradiction analysis

#### Slow Research Times
**Symptoms:** Research takes too long to complete
**Solutions:**
- Reduce max sources limit
- Enable caching
- Use parallel processing
- Optimize source selection

#### Contradiction Errors
**Symptoms:** Conflicting information not properly resolved
**Solutions:**
- Adjust contradiction detection sensitivity
- Review source credibility scoring
- Enable manual conflict resolution

### Performance Tuning

#### For Speed
```json
{
  "max_sources": 20,
  "enable_caching": true,
  "parallel_requests": 5,
  "timeout_seconds": 30
}
```

#### For Quality
```json
{
  "credibility_threshold": 0.9,
  "max_sources": 50,
  "enable_contradiction_analysis": true,
  "academic_prioritization": true
}
```

## Contributing

### Adding New Search Providers
1. Implement the `SearchProvider` interface
2. Add API integration logic
3. Include rate limiting and error handling
4. Add to configuration options

### Enhancing Quality Assessment
1. Implement new credibility metrics
2. Add content quality algorithms
3. Integrate fact-checking services
4. Validate against benchmark datasets

### Improving Report Generation
1. Add new report templates
2. Implement visualization options
3. Enhance executive summary generation
4. Add export format support

## License and Attribution

This skill builds upon ClaudeCode Cowork's research methodologies and extends them with additional capabilities for comprehensive web research.

## Changelog

### v1.0.0
- Initial release with multi-source integration
- Basic quality assessment and contradiction detection
- Structured report generation
- Command-line interface

### Future Releases
- Web interface integration
- Real-time collaboration features
- Advanced visualization options
- Machine learning-enhanced quality assessment
- Multi-language support

---

**Transform your web searches into comprehensive research with the Web Search Deepresearch skill!** 🔍📊🚀