---
name: cowork-productivity-assistant
description: ClaudeCode Cowork-style productivity automation with file management, data analysis, browser operations, and autonomous task execution. This skill should be used when automating office productivity tasks, organizing files, analyzing data, scraping web content, or managing workflow automation. Use for document processing, data insights, web automation, and general productivity enhancement.
---

# Cowork Productivity Assistant

This skill brings ClaudeCode Cowork's revolutionary productivity automation capabilities to Codex, enabling non-technical users to automate complex office workflows through natural language instructions. Inspired by Anthropic's 2026 Cowork release, it provides a comprehensive productivity companion that autonomously handles file organization, data analysis, web automation, and multi-step task execution while maintaining strict safety controls and user oversight.

## Core Features

### Agentic Task Execution
- **Natural Language Processing**: Understand and execute tasks described in plain language
- **Autonomous Planning**: Automatically break down complex tasks into executable steps
- **Multi-step Automation**: Execute sequences of operations with proper dependencies
- **Progress Transparency**: Provide real-time updates on task execution status

### Intelligent File Management
- **Folder-based Access Control**: Operate within user-specified folders with granular permissions
- **Document Processing**: Handle Word, Excel, PowerPoint, PDF, and other common formats
- **Smart Organization**: Automatically categorize and organize files based on content and metadata
- **Safe Operations**: All file modifications require user confirmation for destructive actions

### Data Analysis & Visualization
- **Automated Data Processing**: Parse and analyze data from various sources
- **Statistical Analysis**: Generate insights with descriptive statistics and correlations
- **Intelligent Visualization**: Create charts and graphs automatically
- **Report Generation**: Produce formatted reports and summaries

### Browser Automation & Web Integration
- **Web Scraping**: Extract data from websites with intelligent parsing
- **Form Automation**: Automatically fill and submit web forms
- **Content Aggregation**: Collect and synthesize information from multiple sources
- **Screenshot Intelligence**: Capture and analyze visual content

### Safety & Control Framework
- **Scoped Access**: Operate only within explicitly granted permissions
- **Confirmation Prompts**: Require user approval for high-risk operations
- **Audit Logging**: Maintain comprehensive logs of all operations
- **Recovery Mechanisms**: Provide rollback capabilities for failed operations

## Usage Examples

### File Organization Automation
```bash
# Automatically organize a messy downloads folder
python tools/cowork_productivity_assistant.py organize-files \
  --folder "~/Downloads" \
  --rules "group_by_type,remove_duplicates,clean_names" \
  --confirm-destructive \
  --create-summary
```

### Data Analysis from Screenshots
```bash
# Analyze receipt images and create expense report
python tools/cowork_productivity_assistant.py analyze-receipts \
  --images "~/Pictures/receipts/*.jpg" \
  --extract-data "date,amount,vendor" \
  --generate-report "monthly_expenses.xlsx" \
  --categorize-expenses \
  --create-visualizations
```

### Web Research & Content Aggregation
```bash
# Research topic and create comprehensive summary
python tools/cowork_productivity_assistant.py research-topic \
  --topic "renewable energy trends 2026" \
  --sources "google,scholar,news" \
  --depth "comprehensive" \
  --output-format "markdown_report" \
  --include-sources \
  --generate-timeline
```

### Workflow Automation
```bash
# Automate weekly report generation
python tools/cowork_productivity_assistant.py automate-workflow \
  --name "weekly_sales_report" \
  --steps "collect_data,analyze_trends,generate_charts,create_pdf,send_email" \
  --schedule "weekly_friday_5pm" \
  --error-handling "retry_on_failure,notify_on_error" \
  --backup-results
```

### Document Processing Pipeline
```bash
# Process incoming documents automatically
python tools/cowork_productivity_assistant.py process-documents \
  --input-folder "~/Documents/Inbox" \
  --processing-rules "extract_text,categorize,classify_sentiment" \
  --output-formats "pdf,json,summary" \
  --archive-processed \
  --notify-completion
```

## Task Interpretation & Planning Engine

### Natural Language Task Processing
```python
class TaskInterpreter:
    def interpret_natural_language_task(self, task_description: str,
                                      user_context: UserContext) -> InterpretedTask:
        # Parse task description
        parsed_task = self.parse_task_description(task_description)

        # Extract entities and intent
        entities = self.extract_entities(parsed_task)
        intent = self.classify_intent(parsed_task, entities)

        # Validate task feasibility
        validation = self.validate_task_feasibility(intent, entities, user_context)

        # Generate execution plan
        if validation.feasible:
            execution_plan = self.generate_execution_plan(intent, entities, user_context)
        else:
            execution_plan = None

        return InterpretedTask(
            original_description=task_description,
            parsed_task=parsed_task,
            entities=entities,
            intent=intent,
            validation=validation,
            execution_plan=execution_plan,
            confidence_score=self.calculate_confidence(parsed_task, entities, intent)
        )

    def parse_task_description(self, description: str) -> ParsedTask:
        # Tokenization and normalization
        tokens = self.tokenize_and_normalize(description)

        # Part-of-speech tagging
        pos_tags = self.perform_pos_tagging(tokens)

        # Dependency parsing
        dependencies = self.parse_dependencies(tokens, pos_tags)

        # Semantic role labeling
        semantic_roles = self.label_semantic_roles(tokens, dependencies)

        return ParsedTask(
            tokens=tokens,
            pos_tags=pos_tags,
            dependencies=dependencies,
            semantic_roles=semantic_roles,
            key_phrases=self.extract_key_phrases(tokens, semantic_roles)
        )
```

### Execution Planning & Coordination
```python
class ExecutionPlanner:
    def generate_execution_plan(self, intent: TaskIntent,
                              entities: List[TaskEntity],
                              user_context: UserContext) -> ExecutionPlan:
        # Identify required capabilities
        required_capabilities = self.identify_capabilities(intent, entities)

        # Determine execution sequence
        execution_sequence = self.determine_execution_sequence(
            required_capabilities, entities
        )

        # Allocate resources
        resource_allocation = self.allocate_resources(
            execution_sequence, user_context
        )

        # Create checkpoints
        checkpoints = self.create_execution_checkpoints(execution_sequence)

        # Define success criteria
        success_criteria = self.define_success_criteria(intent, entities)

        # Plan error handling
        error_handling = self.plan_error_handling(execution_sequence)

        return ExecutionPlan(
            intent=intent,
            entities=entities,
            execution_sequence=execution_sequence,
            resource_allocation=resource_allocation,
            checkpoints=checkpoints,
            success_criteria=success_criteria,
            error_handling=error_handling,
            estimated_duration=self.estimate_duration(execution_sequence),
            risk_assessment=self.assess_execution_risks(execution_sequence)
        )

    def identify_capabilities(self, intent: TaskIntent, entities: List[TaskEntity]) -> List[Capability]:
        capabilities = []

        # File management capabilities
        if self.requires_file_operations(intent, entities):
            capabilities.append(Capability.FILE_MANAGEMENT)

        # Data analysis capabilities
        if self.requires_data_analysis(intent, entities):
            capabilities.append(Capability.DATA_ANALYSIS)

        # Web automation capabilities
        if self.requires_web_operations(intent, entities):
            capabilities.append(Capability.WEB_AUTOMATION)

        # Document processing capabilities
        if self.requires_document_processing(intent, entities):
            capabilities.append(Capability.DOCUMENT_PROCESSING)

        return capabilities
```

## File Management & Organization System

### Intelligent File Organization
```python
class FileOrganizationEngine:
    def organize_files_intelligently(self, folder_path: str,
                                   organization_config: OrganizationConfig) -> OrganizationResult:
        # Scan folder contents
        file_inventory = self.scan_folder_contents(folder_path)

        # Analyze file metadata and content
        file_analysis = self.analyze_files(file_inventory)

        # Categorize files
        file_categories = self.categorize_files(file_analysis, organization_config)

        # Generate organization plan
        organization_plan = self.generate_organization_plan(
            file_categories, organization_config
        )

        # Validate safety
        safety_validation = self.validate_organization_safety(organization_plan)

        # Execute organization
        if safety_validation.approved:
            execution_result = self.execute_organization(organization_plan)
            return execution_result
        else:
            return OrganizationResult(
                success=False,
                safety_concerns=safety_validation.concerns,
                suggested_alternatives=safety_validation.alternatives
            )

    def categorize_files(self, file_analysis: Dict[str, FileAnalysis],
                        config: OrganizationConfig) -> Dict[str, List[str]]:
        categories = defaultdict(list)

        for file_path, analysis in file_analysis.items():
            # Content-based categorization
            content_category = self.categorize_by_content(analysis)

            # Metadata-based categorization
            metadata_category = self.categorize_by_metadata(analysis)

            # Type-based categorization
            type_category = self.categorize_by_file_type(analysis)

            # Combine categorizations
            final_category = self.resolve_category_conflicts(
                content_category, metadata_category, type_category, config
            )

            categories[final_category].append(file_path)

        return dict(categories)
```

### Document Processing Pipeline
```python
class DocumentProcessingPipeline:
    def process_document_batch(self, document_paths: List[str],
                             processing_config: ProcessingConfig) -> ProcessingResult:
        results = []

        for doc_path in document_paths:
            # Load document
            document = self.load_document(doc_path)

            # Extract text content
            text_content = self.extract_text_content(document)

            # Analyze document structure
            structure_analysis = self.analyze_document_structure(document)

            # Extract metadata
            metadata = self.extract_document_metadata(document, doc_path)

            # Apply processing rules
            processed_content = self.apply_processing_rules(
                text_content, structure_analysis, metadata, processing_config
            )

            # Generate insights
            insights = self.generate_document_insights(
                processed_content, structure_analysis, metadata
            )

            results.append(DocumentProcessingResult(
                original_path=doc_path,
                processed_content=processed_content,
                metadata=metadata,
                insights=insights,
                processing_steps=self.get_processing_steps()
            ))

        # Aggregate results
        aggregated_result = self.aggregate_processing_results(results)

        return aggregated_result

    def extract_text_content(self, document: Document) -> str:
        # Handle different document formats
        if isinstance(document, PDFDocument):
            return self.extract_pdf_text(document)
        elif isinstance(document, WordDocument):
            return self.extract_word_text(document)
        elif isinstance(document, ExcelDocument):
            return self.extract_excel_text(document)
        else:
            return self.extract_generic_text(document)
```

## Data Analysis & Intelligence Engine

### Automated Data Analysis
```python
class DataAnalysisEngine:
    def perform_comprehensive_analysis(self, data_source: DataSource,
                                     analysis_config: AnalysisConfig) -> AnalysisReport:
        # Data ingestion and validation
        validated_data = self.ingest_and_validate_data(data_source)

        # Statistical analysis
        statistical_summary = self.perform_statistical_analysis(validated_data)

        # Pattern recognition
        patterns = self.identify_patterns(validated_data, analysis_config)

        # Anomaly detection
        anomalies = self.detect_anomalies(validated_data)

        # Predictive modeling (if applicable)
        predictions = self.generate_predictions(validated_data, analysis_config)

        # Generate visualizations
        visualizations = self.create_visualizations(
            validated_data, statistical_summary, patterns, anomalies
        )

        # Generate insights
        insights = self.generate_actionable_insights(
            statistical_summary, patterns, anomalies, predictions
        )

        # Create comprehensive report
        report = self.compile_analysis_report(
            validated_data, statistical_summary, patterns,
            anomalies, predictions, visualizations, insights
        )

        return report

    def identify_patterns(self, data: pd.DataFrame, config: AnalysisConfig) -> List[Pattern]:
        patterns = []

        # Trend analysis
        trends = self.analyze_trends(data, config.time_columns)
        if trends:
            patterns.extend(trends)

        # Correlation analysis
        correlations = self.analyze_correlations(data, config.numeric_columns)
        if correlations:
            patterns.extend(correlations)

        # Clustering analysis
        if config.enable_clustering and len(data) > config.min_cluster_size:
            clusters = self.perform_clustering(data, config)
            patterns.extend(clusters)

        # Seasonal patterns
        if config.enable_seasonal_analysis:
            seasonal_patterns = self.analyze_seasonal_patterns(data, config)
            patterns.extend(seasonal_patterns)

        return patterns
```

### Intelligent Visualization Generation
```python
class VisualizationEngine:
    def generate_smart_visualizations(self, data: pd.DataFrame,
                                    analysis_results: AnalysisResults) -> List[Visualization]:
        visualizations = []

        # Determine appropriate chart types
        chart_types = self.determine_chart_types(data, analysis_results)

        for chart_type in chart_types:
            # Generate visualization specification
            viz_spec = self.create_visualization_spec(chart_type, data, analysis_results)

            # Optimize for readability
            optimized_spec = self.optimize_visualization(viz_spec)

            # Generate visualization
            visualization = self.render_visualization(optimized_spec)

            visualizations.append(visualization)

        # Create dashboard layout
        dashboard = self.create_dashboard_layout(visualizations)

        return visualizations + [dashboard]

    def determine_chart_types(self, data: pd.DataFrame,
                            analysis_results: AnalysisResults) -> List[str]:
        chart_types = []

        # Data type analysis
        data_types = self.analyze_data_types(data)

        # Statistical properties
        stats = analysis_results.statistical_summary

        # Pattern types
        patterns = analysis_results.patterns

        # Recommend chart types based on data characteristics
        if data_types.has_time_series:
            chart_types.append('line_chart')
            if patterns.has_seasonality:
                chart_types.append('seasonal_decomposition')

        if data_types.has_categories:
            chart_types.append('bar_chart')
            if len(data.select_dtypes(include=['category', 'object']).columns) > 1:
                chart_types.append('heatmap')

        if data_types.has_numeric and stats.has_correlations:
            chart_types.append('correlation_matrix')
            chart_types.append('scatter_plot')

        if patterns.has_clusters:
            chart_types.append('cluster_plot')

        return chart_types[:5]  # Limit to top 5 recommendations
```

## Browser Automation & Web Integration

### Intelligent Web Scraping
```python
class WebAutomationEngine:
    async def perform_intelligent_scraping(self, scraping_config: ScrapingConfig) -> ScrapingResult:
        # Initialize browser
        browser = await self.initialize_browser()

        try:
            # Navigate to target
            page = await browser.new_page()
            await page.goto(scraping_config.url)

            # Handle dynamic content
            if scraping_config.wait_for_dynamic:
                await self.wait_for_dynamic_content(page, scraping_config)

            # Extract structured data
            extracted_data = await self.extract_structured_data(page, scraping_config)

            # Process and clean data
            processed_data = self.process_extracted_data(extracted_data, scraping_config)

            # Generate insights
            insights = self.generate_scraping_insights(processed_data, scraping_config)

            return ScrapingResult(
                url=scraping_config.url,
                extracted_data=processed_data,
                insights=insights,
                metadata={
                    'scraping_duration': time.time() - start_time,
                    'pages_processed': 1,
                    'data_points': len(processed_data)
                }
            )

        finally:
            await browser.close()

    async def extract_structured_data(self, page: Page,
                                    config: ScrapingConfig) -> Dict[str, Any]:
        extracted_data = {}

        # Extract by selectors
        if config.selectors:
            for field_name, selector in config.selectors.items():
                elements = await page.query_selector_all(selector)
                extracted_data[field_name] = [
                    await element.text_content() for element in elements
                ]

        # Extract tables
        if config.extract_tables:
            tables = await self.extract_tables(page)
            extracted_data['tables'] = tables

        # Extract structured data (JSON-LD, Microdata)
        if config.extract_structured:
            structured_data = await self.extract_structured_data(page)
            extracted_data['structured_data'] = structured_data

        # Take screenshots if needed
        if config.capture_screenshots:
            screenshots = await self.take_targeted_screenshots(page, config)
            extracted_data['screenshots'] = screenshots

        return extracted_data
```

### Form Automation & Interaction
```python
class FormAutomationEngine:
    async def automate_form_interaction(self, form_config: FormConfig) -> AutomationResult:
        browser = await self.initialize_browser()

        try:
            page = await browser.new_page()
            await page.goto(form_config.url)

            # Wait for form to load
            await self.wait_for_form(page, form_config)

            # Fill form fields
            fill_results = await self.fill_form_fields(page, form_config.fields)

            # Handle dynamic elements
            if form_config.has_dynamic_elements:
                await self.handle_dynamic_elements(page, form_config)

            # Submit form
            submit_result = await self.submit_form(page, form_config)

            # Handle post-submission
            post_result = await self.handle_post_submission(page, submit_result, form_config)

            return AutomationResult(
                success=submit_result.success,
                form_data=form_config.fields,
                submit_result=submit_result,
                post_submission_result=post_result,
                screenshots=await self.take_result_screenshots(page)
            )

        finally:
            await browser.close()

    async def fill_form_fields(self, page: Page,
                             fields: Dict[str, FieldConfig]) -> Dict[str, FieldResult]:
        results = {}

        for field_name, field_config in fields.items():
            try:
                # Locate field
                field_element = await self.locate_form_field(page, field_config)

                # Fill field based on type
                if field_config.field_type == 'text':
                    await field_element.fill(field_config.value)
                elif field_config.field_type == 'select':
                    await field_element.select_option(field_config.value)
                elif field_config.field_type == 'checkbox':
                    if field_config.value:
                        await field_element.check()
                    else:
                        await field_element.uncheck()
                elif field_config.field_type == 'radio':
                    await field_element.check()

                results[field_name] = FieldResult(
                    success=True,
                    field_type=field_config.field_type,
                    value=field_config.value
                )

            except Exception as e:
                results[field_name] = FieldResult(
                    success=False,
                    error=str(e),
                    field_type=field_config.field_type
                )

        return results
```

## Safety & Control Framework

### Permission Management System
```python
class PermissionManager:
    def validate_operation_permissions(self, operation: Operation,
                                     user_permissions: UserPermissions) -> PermissionResult:
        # Check operation type permissions
        operation_allowed = self.check_operation_type_permission(operation, user_permissions)

        # Check resource-specific permissions
        resource_allowed = self.check_resource_permissions(operation, user_permissions)

        # Check scope limitations
        scope_allowed = self.check_scope_limitations(operation, user_permissions)

        # Aggregate permission results
        overall_allowed = operation_allowed and resource_allowed and scope_allowed

        # Generate permission explanation
        explanation = self.generate_permission_explanation(
            operation, operation_allowed, resource_allowed, scope_allowed
        )

        return PermissionResult(
            allowed=overall_allowed,
            operation_allowed=operation_allowed,
            resource_allowed=resource_allowed,
            scope_allowed=scope_allowed,
            explanation=explanation,
            required_permissions=self.get_required_permissions(operation)
        )

    def check_resource_permissions(self, operation: Operation,
                                 permissions: UserPermissions) -> bool:
        # File system permissions
        if operation.resource_type == ResourceType.FILE:
            return self.check_file_permissions(operation.path, permissions.file_permissions)

        # Network permissions
        elif operation.resource_type == ResourceType.NETWORK:
            return self.check_network_permissions(operation.url, permissions.network_permissions)

        # System permissions
        elif operation.resource_type == ResourceType.SYSTEM:
            return self.check_system_permissions(operation.command, permissions.system_permissions)

        return False
```

### Confirmation & Audit System
```python
class ConfirmationAuditSystem:
    def request_user_confirmation(self, operation: Operation,
                                risk_assessment: RiskAssessment) -> ConfirmationResult:
        # Assess operation risk
        risk_level = self.assess_operation_risk(operation)

        # Determine confirmation requirements
        requires_confirmation = self.requires_user_confirmation(risk_level, operation)

        if requires_confirmation:
            # Generate confirmation dialog
            confirmation_dialog = self.generate_confirmation_dialog(operation, risk_assessment)

            # Present to user and wait for response
            user_response = await self.present_confirmation_dialog(confirmation_dialog)

            # Log confirmation request
            self.log_confirmation_request(operation, user_response)

            return ConfirmationResult(
                confirmed=user_response.confirmed,
                user_id=user_response.user_id,
                timestamp=user_response.timestamp,
                risk_level=risk_level,
                operation_details=operation
            )
        else:
            # Auto-approve low-risk operations
            return ConfirmationResult(
                confirmed=True,
                auto_approved=True,
                risk_level=risk_level,
                operation_details=operation
            )

    def assess_operation_risk(self, operation: Operation) -> RiskLevel:
        risk_score = 0

        # File operation risks
        if operation.type == OperationType.FILE_MODIFY:
            risk_score += self.calculate_file_modification_risk(operation)
        elif operation.type == OperationType.FILE_DELETE:
            risk_score += self.calculate_file_deletion_risk(operation)

        # Network operation risks
        if operation.type == OperationType.NETWORK_ACCESS:
            risk_score += self.calculate_network_access_risk(operation)

        # System operation risks
        if operation.type == OperationType.SYSTEM_COMMAND:
            risk_score += self.calculate_system_command_risk(operation)

        # Data sensitivity risks
        risk_score += self.calculate_data_sensitivity_risk(operation)

        # Determine risk level
        if risk_score >= 80:
            return RiskLevel.CRITICAL
        elif risk_score >= 60:
            return RiskLevel.HIGH
        elif risk_score >= 40:
            return RiskLevel.MEDIUM
        elif risk_score >= 20:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
```

## Resident Agent Integration

### Background Service Architecture
```python
class ResidentCoworkAgent:
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.execution_engine = ExecutionEngine()
        self.notification_manager = NotificationManager()
        self.system_monitor = SystemMonitor()
        self.power_manager = PowerManager()

    async def run_resident_service(self):
        """Main resident agent loop"""
        # Initialize system integration
        await self.initialize_system_integration()

        # Start background tasks
        background_tasks = [
            self.process_task_queue(),
            self.monitor_system_resources(),
            self.handle_system_events(),
            self.perform_maintenance_tasks(),
            self.update_agent_knowledge()
        ]

        # Run all background tasks concurrently
        await asyncio.gather(*background_tasks, return_exceptions=True)

    async def process_task_queue(self):
        """Process queued tasks"""
        while True:
            try:
                # Get next task with timeout
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )

                # Process task asynchronously
                asyncio.create_task(self.process_individual_task(task))

            except asyncio.TimeoutError:
                # No tasks available, continue monitoring
                continue
            except Exception as e:
                logger.error(f"Error processing task queue: {e}")
                await asyncio.sleep(1)

    async def process_individual_task(self, task: CoworkTask):
        """Process individual task with full lifecycle"""
        try:
            # Task initialization
            await self.initialize_task_execution(task)

            # Interpret and plan
            interpreted_task = await self.interpret_task(task)
            execution_plan = await self.create_execution_plan(interpreted_task)

            # Execute with monitoring
            execution_result = await self.execute_task_with_monitoring(
                interpreted_task, execution_plan
            )

            # Post-execution processing
            await self.process_execution_result(task, execution_result)

        except Exception as e:
            # Handle execution errors
            await self.handle_task_execution_error(task, e)
        finally:
            # Cleanup task resources
            await self.cleanup_task_resources(task)

    async def monitor_system_resources(self):
        """Monitor system resources and adjust behavior"""
        while True:
            # Check system resources
            resources = await self.system_monitor.check_resources()

            # Adjust processing based on resources
            if resources.cpu_usage > 80:
                await self.throttle_processing()
            elif resources.memory_usage > 90:
                await self.free_memory()

            # Update performance metrics
            await self.update_performance_metrics(resources)

            await asyncio.sleep(30)  # Check every 30 seconds
```

## GUI Bridge & User Interface

### Natural Language Task Interface
```jsx
// CoworkTaskInterface.jsx
function CoworkTaskInterface({ agent }) {
  const [taskInput, setTaskInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentTask, setCurrentTask] = useState(null);
  const [taskHistory, setTaskHistory] = useState([]);

  const handleTaskSubmit = async () => {
    if (!taskInput.trim()) return;

    setIsProcessing(true);
    try {
      // Submit task to agent
      const taskResult = await agent.submitTask({
        description: taskInput,
        timestamp: new Date(),
        priority: 'normal'
      });

      setCurrentTask(taskResult);
      setTaskInput('');

      // Monitor task progress
      monitorTaskProgress(taskResult.id);

    } catch (error) {
      console.error('Task submission failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const monitorTaskProgress = (taskId) => {
    const progressInterval = setInterval(async () => {
      const status = await agent.getTaskStatus(taskId);
      setCurrentTask(prev => ({ ...prev, status }));

      if (status.completed || status.failed) {
        clearInterval(progressInterval);
        setTaskHistory(prev => [status, ...prev]);
        setCurrentTask(null);
      }
    }, 1000);
  };

  return (
    <div className="cowork-interface">
      <div className="task-input-section">
        <textarea
          value={taskInput}
          onChange={(e) => setTaskInput(e.target.value)}
          placeholder="何を自動化しますか？（例: ダウンロードフォルダを整理してレポートを作成）"
          disabled={isProcessing}
          className="task-input"
        />
        <button
          onClick={handleTaskSubmit}
          disabled={isProcessing || !taskInput.trim()}
          className="submit-button"
        >
          {isProcessing ? '処理中...' : '実行'}
        </button>
      </div>

      {currentTask && (
        <TaskProgressMonitor
          task={currentTask}
          onCancel={() => agent.cancelTask(currentTask.id)}
        />
      )}

      <TaskHistory
        tasks={taskHistory}
        onRetry={(task) => setTaskInput(task.description)}
      />
    </div>
  );
}
```

### Progress Monitoring & Control
```jsx
// TaskProgressMonitor.jsx
function TaskProgressMonitor({ task, onCancel }) {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const updateInterval = setInterval(async () => {
      const status = await agent.getDetailedTaskStatus(task.id);
      setProgress(status.progress);
      setCurrentStep(status.currentStep);
      setLogs(status.logs);
    }, 500);

    return () => clearInterval(updateInterval);
  }, [task.id]);

  return (
    <div className="task-monitor">
      <div className="progress-header">
        <h3>タスク実行中: {task.description}</h3>
        <button onClick={onCancel} className="cancel-button">
          キャンセル
        </button>
      </div>

      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${progress}%` }}
        />
        <span className="progress-text">{progress}%</span>
      </div>

      <div className="current-step">
        <strong>現在のステップ:</strong> {currentStep}
      </div>

      <div className="execution-logs">
        <h4>実行ログ</h4>
        <div className="logs-container">
          {logs.map((log, index) => (
            <div key={index} className={`log-entry ${log.level}`}>
              <span className="timestamp">{log.timestamp}</span>
              <span className="message">{log.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

## Success Metrics & Quality Assurance

### Performance Metrics
- **Task Completion Rate**: > 95% successful task execution
- **Response Time**: < 3 seconds for task interpretation
- **Resource Efficiency**: < 200MB memory usage during operation
- **User Satisfaction**: > 4.5/5.0 interface usability rating

### Safety Metrics
- **Permission Compliance**: 100% adherence to user permissions
- **Data Protection**: 0 data loss incidents
- **Audit Coverage**: 100% operations logged and auditable
- **Recovery Success**: > 98% successful error recovery

### Productivity Metrics
- **Time Savings**: 70% reduction in manual productivity tasks
- **Error Reduction**: 80% fewer manual errors in automated processes
- **Consistency**: 100% consistent execution of repetitive tasks
- **Scalability**: Support for 50+ concurrent automation tasks

## Conclusion

The Cowork Productivity Assistant represents the future of AI-assisted productivity, bringing ClaudeCode Cowork's autonomous automation capabilities to the Codex ecosystem. By combining natural language task processing, intelligent file management, automated data analysis, and safe web integration, it empowers users to automate complex productivity workflows with unprecedented ease and reliability.

This skill serves as the intelligent productivity companion that understands user intent, executes complex workflows autonomously, and maintains the highest standards of safety, transparency, and user control. Through seamless GUI integration and resident operation, it transforms how users interact with their digital workspaces, making automation accessible to everyone while preserving human oversight and creativity.