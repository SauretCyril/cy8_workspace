# 🔍 RAPPORT D'AUDIT DU CODE - cy8_workspace
======================================================================

## 📊 STATISTIQUES GLOBALES
----------------------------------------------------------------------
📁 Fichiers Python: 23
📝 Lignes de code totales: 21,285
⚙️  Fonctions totales: 577
🏗️  Classes totales: 24
🔤 Noms de fonctions uniques: 526
🔤 Noms de classes uniques: 24

## 🔄 FONCTIONS EN DOUBLON
----------------------------------------------------------------------
⚠️  29 fonctions définies plusieurs fois:

**Note importante:** Certains "doublons" sont en fait une **architecture MVC correcte** où une fonction UI appelle une fonction DB du même nom. Ces cas sont marqués ✅ **FAUX POSITIF**.

### `add_environment` (2 définitions) ✅ **FAUX POSITIF - Architecture correcte**
   - src\cy8_database_manager.py:1000 - Fonction DB (insert SQL)
   - src\cy8_prompts_manager_main.py:7117 - Fonction UI (dialogue + appelle DB)
   - **Note:** Séparation des responsabilités (MVC) - Les deux sont utilisées

### `cancel` (4 définitions)
   - src\cy8_popup_manager.py:304
   - src\cy8_popup_manager.py:543
   - src\cy8_prompts_manager_main.py:11845
   - src\cy8_prompts_manager_main.py:4735

### `center_window` (2 définitions)
   - src\cy8_popup_manager.py:14
   - src\cy8_prompts_manager_main.py:12

### `clear_recent_databases` (2 définitions)
   - src\cy8_prompts_manager_main.py:5035
   - src\cy8_user_preferences.py:169

### `close` (3 définitions)
   - src\cy8_comfyui_customNode_call.py:536
   - src\cy8_database_manager.py:773
   - src\cy8_image_index_manager.py:550

### `close_popup` (2 définitions)
   - src\cy8_popup_id_manager.py:106
   - src\cy8_prompts_manager_main.py:51

### `delete_environment` (2 définitions) ✅ **FAUX POSITIF - Architecture correcte**
   - src\cy8_database_manager.py:1062 - Fonction DB (DELETE SQL)
   - src\cy8_prompts_manager_main.py:7238 - Fonction UI (confirmation + appelle DB)
   - **Note:** Même pattern MVC que add_environment - Les deux sont utilisées

### `delete_prompt` (2 définitions) ✅ **FAUX POSITIF - Architecture correcte**
   - src\cy8_database_manager.py:545 - Fonction DB (DELETE SQL)
   - src\cy8_prompts_manager_main.py:3580 - Fonction UI (menu + bouton)
   - **Note:** Pattern MVC - Les deux sont utilisées

### `edit_inputs_popup` (2 définitions)
   - src\cy8_editable_tables.py:16
   - src\cy8_editable_tables.py:487

### `get_all_extra_paths` (2 définitions)
   - src\cy8_paths.py:256
   - src\cy8_paths.py:46

### `get_current_focus` (3 définitions)
   - src\cy8_rag_manager.py:1287
   - src\cy8_rag_manager.py:1598
   - src\cy8_todo_manager.py:228

### `get_default_db_path` (2 définitions)
   - src\cy8_paths.py:231
   - src\cy8_paths.py:86

### `get_environment_analyses_directory` (2 définitions)
   - src\cy8_database_manager.py:911
   - src\cy8_rag_manager.py:1300

### `get_popup_id` (2 définitions)
   - src\cy8_popup_id_manager.py:101
   - src\cy8_prompts_manager_main.py:49

### `is_todo_command` (2 définitions)
   - src\cy8_rag_manager.py:1266
   - src\cy8_rag_manager.py:1604

### `main` (3 définitions)
   - src\cy8_preferences_manager.py:106
   - src\cy8_prompts_manager_main.py:11850
   - src\cy8_rag_manager.py:1294

### `normalize_path` (2 définitions)
   - src\cy8_paths.py:236
   - src\cy8_paths.py:110

### `on_save` (3 définitions)
   - src\cy8_editable_tables.py:393
   - src\cy8_prompts_manager_main.py:3449
   - src\cy8_prompts_manager_main.py:3471

### `process_todo_command` (2 définitions)
   - src\cy8_rag_manager.py:1108
   - src\cy8_rag_manager.py:1412

### `restore_chat_history` (2 définitions)
   - src\cy8_prompts_manager_main.py:9353
   - src\cy8_todo_manager.py:299

### `run_test` (4 définitions)
   - src\cy8_prompts_manager_main.py:11311
   - src\cy8_prompts_manager_main.py:11373
   - src\cy8_prompts_manager_main.py:11395
   - src\cy8_prompts_manager_main.py:11417

### `run_tests` (2 définitions)
   - src\cy8_prompts_manager_main.py:11260
   - src\cy8_test_suite.py:332

### `save_edit` (2 définitions)
   - src\cy8_editable_tables.py:347
   - src\cy8_popup_manager.py:483

### `setUp` (2 définitions)
   - src\cy8_test_suite.py:26
   - src\cy8_test_suite.py:244

### `set_extra_paths` (2 définitions)
   - src\cy8_paths.py:246
   - src\cy8_paths.py:18

### `setup_ui` (2 définitions)
   - src\cy8_prompts_manager_main.py:249
   - src\cy8_prompts_manager_main.py:11649

### `show_error` (2 définitions)
   - src\cy8_prompts_manager_main.py:9638
   - src\cy8_prompts_manager_main.py:10192

### `show_timeout` (2 définitions)
   - src\cy8_prompts_manager_main.py:9632
   - src\cy8_prompts_manager_main.py:10200

### `tearDown` (2 définitions)
   - src\cy8_test_suite.py:33
   - src\cy8_test_suite.py:250


## 🔄 CLASSES EN DOUBLON
----------------------------------------------------------------------
✅ Aucune classe en doublon détectée

## 👻 FONCTIONS ORPHELINES (POTENTIELLEMENT FANTÔMES)
----------------------------------------------------------------------
⚠️  401 fonctions jamais appelées (ou seulement en interne):

### src\cy6_file.py
   - `save_json` (ligne 12)

### src\cy6_task_comfyui.py
   - `log_values` (ligne 23)

### Les fonctions cy6_websocket_api_client doivent restée
### pour une utilisation future
### src\cy6_websocket_api_client.py
   - `get_image` (ligne 39)
   - `get_history` (ligne 48)
   - `get_queue_status` (ligne 55)
   - `resolve_path` (ligne 105)
   - `server_get_prompt` (ligne 280)
   - `socket_queue_add` (ligne 314)
   - `get_history_images` (ligne 385)
   - `server_get_infLora` (ligne 403)

### src\cy6_wkf001_Basic.py
   - `run_now` (ligne 17)

### Les fonctions cy8_comfyui_customNode_call doivent restée
### pour une utilisation future
### src\cy8_comfyui_customNode_call.py
   - `get_custom_nodes_info` (ligne 50)
   - `get_available_custom_node_types` (ligne 69)
   - `_is_custom_node` (ligne 92)
   - `create_custom_node_workflow` (ligne 119)
   - `execute_custom_node_workflow` (ligne 168)
   - `get_extra_paths` (ligne 396)
   - `get_custom_node_schema` (ligne 466)
   - `validate_custom_node_inputs` (ligne 485)
   - `example_usage` (ligne 608)

### src\cy8_database_manager.py
   - `ensure_additional_columns` (ligne 215)
   - `remove_legacy_image_column` (ligne 299)
   - `add_default_basic_prompt` (ligne 376)
   - `normalize` (ligne 468)
   - `extract_model_name` (ligne 473)
   - `fix_database_structure` (ligne 604)
   - `get_images_by_environment` (ligne 733)
   - `delete_prompt_images` (ligne 761)
   - `ensure_environment_tables` (ligne 778)
   - `add_default_environments` (ligne 839)
   - `get_environment_by_id` (ligne 982)
   - `add_environment` (ligne 1000)
   - `delete_environment` (ligne 1062)

### src\cy8_editable_tables.py
   - `edit_inputs_popup` (ligne 16)
   - `on_values_double_click` (ligne 263)
   - `on_workflow_double_click` (ligne 307)
   - `edit_cell_inline` (ligne 330)
   - `save_edit` (ligne 347)
   - `cancel_edit` (ligne 363)
   - `show_output_images` (ligne 370)
   - `edit_multiloras` (ligne 390)
   - `edit_value_popup` (ligne 408)
   - `save_value` (ligne 461)
   - `edit_inputs_popup` (ligne 487)
   - `refresh_inputs_table` (ligne 559)
   - `add_input` (ligne 579)
   - `edit_input` (ligne 587)
   - `save_input` (ligne 630)
   - `delete_input` (ligne 662)
   - `save_inputs` (ligne 693)
   - `add_prompt_value` (ligne 716)
   - `delete_prompt_value` (ligne 729)
   - `add_workflow_node` (ligne 745)
   - `delete_workflow_node` (ligne 765)
   - `update_values_data` (ligne 781)
   - `update_workflow_data` (ligne 792)
   - `_save_current_prompt` (ligne 819)

### src\cy8_fast_image_processor.py
   - `create_thumbnail` (ligne 42)
   - `_create_thumbnail_pil` (ligne 64)
   - `get_dimensions` (ligne 84)
   - `calculate_hash` (ligne 106)
   - `create_thumbnail_fast` (ligne 160)
   - `get_image_dimensions_fast` (ligne 167)
   - `calculate_image_hash_fast` (ligne 172)

### src\cy8_image_index_manager.py
   - `_init_database` (ligne 50)
   - `_get_file_hash` (ligne 100)
   - `_create_thumbnail` (ligne 112)
   - `_process_image_file` (ligne 208)

### src\cy8_log_analyzer.py
   - `_parse_log_content` (ligne 87)
   - `_extract_timestamp` (ligne 175)
   - `_extract_config_id` (ligne 217)
   - `_extract_custom_node_from_import_line` (ligne 235)
   - `_is_error` (ligne 253)
   - `_extract_error_info` (ligne 266)
   - `_is_warning` (ligne 317)
   - `_extract_warning_info` (ligne 329)
   - `_extract_custom_node_from_error` (ligne 339)
   - `_extract_error_details` (ligne 361)
   - `_extract_loading_time` (ligne 381)
   - `_extract_failure_reason` (ligne 390)
   - `_is_important_info` (ligne 405)
   - `_extract_info` (ligne 420)
   - `_get_analysis_entries` (ligne 424)
   - `get_all_entries` (ligne 510)
   - `test_log_analyzer` (ligne 530)

### src\cy8_mistral.py
   - `analyze_comfyui_error` (ligne 71)
   - `save_error_solution` (ligne 107)
   - `load_error_solution` (ligne 157)

### src\cy8_paths.py
   - `get_extra_path_by_key` (ligne 41)
   - `_get_last_directory_name` (ligne 51)
   - `find_paths_containing` (ligne 68)
   - `get_paths_by_type` (ligne 77)
   - `get_data_directory` (ligne 98)
   - `ensure_directory_exists` (ligne 121)
   - `is_absolute_path` (ligne 134)
   - `get_relative_path` (ligne 139)
   - `path_exists` (ligne 148)
   - `change_file_extension` (ligne 178)
   - `get_file_extension` (ligne 190)
   - `get_extra_path` (ligne 251)

### src\cy8_popup_id_manager.py
   - `get_next_id` (ligne 31)
   - `register_popup` (ligne 38)
   - `unregister_popup` (ligne 58)
   - `get_active_popups` (ligne 68)
   - `get_popup_history` (ligne 73)
   - `format_title` (ligne 78)
   - `print_status` (ligne 85)
   - `get_popup_id` (ligne 101)
   - `close_popup` (ligne 106)

### src\cy8_popup_manager.py
   - `load_json_to_text` (ligne 23)
   - `save_prompt` (ligne 239)
   - `cancel` (ligne 304)
   - `refresh_table` (ligne 389)
   - `add_lora` (ligne 401)
   - `save_lora` (ligne 428)
   - `edit_lora` (ligne 447)
   - `save_edit` (ligne 483)
   - `delete_lora` (ligne 506)
   - `save_multiloras` (ligne 532)
   - `cancel` (ligne 543)

### src\cy8_preferences_manager.py
   - `show_info` (ligne 17)
   - `clean_recent` (ligne 52)
   - `clear_all` (ligne 71)
   - `clear_recent_only` (ligne 83)
   - `set_default_db` (ligne 97)

### src\cy8_prompts_manager_main.py
   - `get_popup_id` (ligne 49)
   - `close_popup` (ligne 51)
   - `restore_saved_environment` (ligne 170)
   - `update_chat_welcome_message` (ligne 196)
   - `add_startup_environment_message` (ligne 205)
   - `add_no_environment_message` (ligne 209)
   - `init_images_paths` (ligne 213)
   - `setup_main_window` (ligne 224)
   - `setup_ui` (ligne 249)
   - `create_menu` (ligne 276)
   - `setup_ribbon` (ligne 337)
   - `toggle_filters_tab` (ligne 513)
   - `show_about` (ligne 534)
   - `setup_prompts_table` (ligne 545)
   - `setup_details_panel` (ligne 599)
   - `setup_filters_tab` (ligne 689)
   - `setup_chat_tab` (ligne 757)
   - `setup_terminal_tab` (ligne 1093)
   - `setup_info_tab` (ligne 1271)
   - `setup_comfyui_tab` (ligne 1357)
   - `setup_log_tab` (ligne 1652)
   - `configure_scroll_region` (ligne 1669)
   - `configure_canvas_width` (ligne 1672)
   - `_on_mousewheel` (ligne 1681)
   - `setup_data_tab` (ligne 2031)
   - `setup_executions_tab` (ligne 2202)
   - `setup_images_tab` (ligne 2293)
   - `setup_prompt_images_tab` (ligne 2317)
   - `setup_gallery_tab` (ligne 2432)
   - `refresh_gallery` (ligne 2580)
   - `refresh_gallery_with_scan` (ligne 2643)
   - `force_refresh_gallery` (ligne 2682)
   - `create_gallery_grid_from_index` (ligne 2724)
   - `_create_default_thumbnail` (ligne 2806)
   - `create_gallery_grid` (ligne 2822)
   - `enlarge_gallery_image` (ligne 2886)
   - `open_image_with_default` (ligne 2981)
   - `select_gallery_image` (ligne 2991)
   - `delete_selected_gallery_image` (ligne 3031)
   - `open_selected_gallery_image` (ligne 3068)
   - `copy_selected_gallery_path` (ligne 3075)
   - `mark_gallery_image_deleted` (ligne 3082)
   - `restore_gallery_image` (ligne 3111)
   - `show_gallery_stats` (ligne 3159)
   - `_clear_cache_and_refresh` (ligne 3229)
   - `on_gallery_tab_selected` (ligne 3239)
   - `copy_path_to_clipboard` (ligne 3261)
   - `setup_status_bar` (ligne 3270)
   - `load_prompts` (ligne 3288)
   - `on_prompt_select` (ligne 3311)
   - `on_prompt_double_click` (ligne 3318)
   - `load_prompt_details` (ligne 3323)
   - `on_data_change` (ligne 3381)
   - `save_current_info` (ligne 3385)
   - `new_prompt` (ligne 3446)
   - `edit_prompt` (ligne 3465)
   - `inherit_prompt` (ligne 3477)
   - `execute_workflow` (ligne 3607)
   - `_execute_workflow_task` (ligne 3670)
   - `update_prompt_status_after_execution` (ligne 3904)
   - `open_prompt_analysis` (ligne 3943)
   - `add_to_execution_stack` (ligne 4042)
   - `update_execution_stack_status` (ligne 4057)
   - `update_execution_display` (ligne 4071)
   - `update_executions_tree` (ligne 4085)
   - `clear_execution_history` (ligne 4112)
   - `on_execution_select` (ligne 4123)
   - `refresh_images_list` (ligne 4164)
   - `on_image_select` (ligne 4204)
   - `add_images_to_prompt` (ligne 4241)
   - `enlarge_selected_image` (ligne 4288)
   - `open_selected_image` (ligne 4340)
   - `remove_selected_image` (ligne 4367)
   - `open_images_folder` (ligne 4406)
   - `add_output_images_to_database` (ligne 4508)
   - `clear_details` (ligne 4564)
   - `update_status` (ligne 4581)
   - `update_database_stats` (ligne 4594)
   - `change_database` (ligne 4615)
   - `create_new_database` (ligne 4628)
   - `browse_directory` (ligne 4679)
   - `create_database` (ligne 4696)
   - `cancel` (ligne 4735)
   - `switch_to_database` (ligne 4743)
   - `import_json` (ligne 4803)
   - `export_json` (ligne 4908)
   - `update_recent_databases_menu` (ligne 4995)
   - `open_recent_database` (ligne 5023)
   - `refresh_recent_list` (ligne 5043)
   - `open_selected_recent` (ligne 5058)
   - `remove_selected_recent` (ligne 5088)
   - `on_closing` (ligne 5118)
   - `add_default_filters` (ligne 5138)
   - `add_filter_row` (ligne 5177)
   - `on_filter_type_changed` (ligne 5242)
   - `update_criteria_options` (ligne 5249)
   - `add_new_filter` (ligne 5304)
   - `remove_filter_row` (ligne 5308)
   - `on_filter_changed` (ligne 5316)
   - `apply_filters` (ligne 5321)
   - `apply_single_filter` (ligne 5366)
   - `update_prompts_display` (ligne 5444)
   - `reset_filters` (ligne 5487)
   - `refresh_prompts_display` (ligne 5500)
   - `has_active_filters` (ligne 5525)
   - `open_images_in_explorer` (ligne 5537)
   - `test_comfyui_connection` (ligne 5569)
   - `get_model_metadata` (ligne 5686)
   - `identify_comfyui_environment` (ligne 5705)
   - `_identify_with_custom_node` (ligne 5729)
   - `refresh_env_data` (ligne 6083)
   - `filter_env_paths` (ligne 6132)
   - `copy_selected_path` (ligne 6187)
   - `_extract_config_id_from_extra_paths` (ligne 6212)
   - `browse_log_file` (ligne 6330)
   - `analyze_comfyui_log` (ligne 6356)
   - `check_log_file_status` (ligne 6551)
   - `update_analysis_buttons_state` (ligne 6590)
   - `set_current_environment` (ligne 6623)
   - `refresh_log_analysis` (ligne 6659)
   - `export_log_analysis` (ligne 6668)
   - `refresh_environments` (ligne 6710)
   - `on_environment_select` (ligne 6769)
   - `on_environment_double_click` (ligne 6788)
   - `open_env_actions_popup` (ligne 6802)
   - `refresh_actions` (ligne 6862)
   - `add_env_action_dialog` (ligne 6917)
   - `save_action` (ligne 6950)
   - `edit_env_action_dialog` (ligne 6972)
   - `save_changes` (ligne 7020)
   - `delete_env_action_dialog` (ligne 7042)
   - `save_env_actions_json` (ligne 7072)
   - `add_environment` (ligne 7117)
   - `edit_environment` (ligne 7168)
   - `delete_environment` (ligne 7238)
   - `load_environment_analysis_results` (ligne 7284)
   - `filter_log_results` (ligne 7441)
   - `search_log_results` (ligne 7485)
   - `show_log_detail` (ligne 7489)
   - `_copy_log_details_to_clipboard` (ligne 7641)
   - `_build_rich_details_for_db` (ligne 7660)
   - `open_solutions_folder` (ligne 7685)
   - `analyze_complete_log_global` (ligne 7710)
   - `on_close` (ligne 7741)
   - `start_global_log_analysis` (ligne 7906)
   - `analyze_in_thread` (ligne 7913)
   - `show_question_examples` (ligne 8005)
   - `use_selected_question` (ligne 8085)
   - `save_global_analysis` (ligne 8117)
   - `validate_rag_environment` (ligne 8221)
   - `audit_rag_environment_consistency` (ligne 8258)
   - `ensure_analysis_has_environment_id` (ligne 8331)
   - `initialize_chat_welcome` (ligne 8355)
   - `add_chat_message` (ligne 8431)
   - `send_chat_message` (ligne 8474)
   - `process_chat_message` (ligne 8494)
   - `handle_add_constraint_request` (ligne 8556)
   - `handle_server_status_request` (ligne 8561)
   - `handle_recurring_errors_request` (ligne 8593)
   - `handle_general_query` (ligne 8614)
   - `on_rag_mode_changed` (ligne 8671)
   - `show_rag_modes_info` (ligne 8689)
   - `_create_mode_info_tab` (ligne 8758)
   - `get_current_rag_mode` (ligne 8787)
   - `set_rag_mode` (ligne 8791)
   - `generate_expert_server_report` (ligne 8797)
   - `create_expert_server_report` (ligne 8820)
   - `get_current_server_status` (ligne 8906)
   - `generate_expert_system_info` (ligne 8925)
   - `generate_expert_error_analysis` (ligne 9054)
   - `generate_expert_optimization_advice` (ligne 9193)
   - `generate_intelligent_response` (ligne 9228)
   - `send_quick_message` (ligne 9277)
   - `clear_chat_input` (ligne 9282)
   - `get_chat_history` (ligne 9286)
   - `clear_chat_history` (ligne 9344)
   - `on_enter_pressed` (ligne 9370)
   - `refresh_chat_context` (ligne 9378)
   - `add_system_constraint` (ligne 9400)
   - `save_constraint` (ligne 9438)
   - `search_error_history` (ligne 9462)
   - `perform_search` (ligne 9479)
   - `detect_python_manually` (ligne 9506)
   - `execute_python_command` (ligne 9556)
   - `run_command` (ligne 9604)
   - `update_result` (ligne 9615)
   - `show_timeout` (ligne 9632)
   - `show_error` (ligne 9638)
   - `scan_and_index_existing_analyses` (ligne 9656)
   - `is_analysis_already_indexed` (ligne 9742)
   - `update_chat_rag_indicators` (ligne 9762)
   - `get_rag_statistics` (ligne 9791)
   - `manual_rag_scan` (ligne 9832)
   - `send_environment_context_to_rag` (ligne 9890)
   - `get_recent_log_analyses` (ligne 9982)
   - `create_rag_context_report` (ligne 10013)
   - `execute_terminal_command` (ligne 10112)
   - `run_command_in_subprocess` (ligne 10147)
   - `run_process` (ligne 10153)
   - `show_output` (ligne 10187)
   - `show_error` (ligne 10192)
   - `show_timeout` (ligne 10200)
   - `read_output` (ligne 10207)
   - `append_line` (ligne 10212)
   - `append_success` (ligne 10236)
   - `append_error` (ligne 10240)
   - `interrupt_terminal_command` (ligne 10261)
   - `change_terminal_directory` (ligne 10275)
   - `browse_terminal_directory` (ligne 10295)
   - `on_terminal_key_press` (ligne 10311)
   - `navigate_terminal_history` (ligne 10329)
   - `append_terminal_output` (ligne 10354)
   - `save_terminal_session` (ligne 10391)
   - `clear_terminal_output` (ligne 10421)
   - `index_terminal_session` (ligne 10434)
   - `toggle_rag_indexing` (ligne 10493)
   - `initialize_terminal_welcome` (ligne 10506)
   - `examine_rag_index` (ligne 10533)
   - `reindex_rag_analyses` (ligne 10602)
   - `reindex_thread` (ligne 10614)
   - `show_rag_statistics` (ligne 10636)
   - `show_current_server_state` (ligne 10692)
   - `show_temporal_analysis` (ligne 10770)
   - `show_temporal_evolution` (ligne 10844)
   - `reset_rag_completely` (ligne 10895)
   - `clean_custom_environments` (ligne 11048)
   - `test_rag_efficiency` (ligne 11109)
   - `run_rag_test_suite` (ligne 11214)
   - `run_tests` (ligne 11260)
   - `run_quick_rag_test` (ligne 11287)
   - `run_test` (ligne 11311)
   - `handle_rag_test_command` (ligne 11338)
   - `handle_quick_test_command` (ligne 11361)
   - `test_rag_indexing` (ligne 11365)
   - `run_test` (ligne 11373)
   - `test_rag_learning` (ligne 11387)
   - `run_test` (ligne 11395)
   - `test_rag_performance` (ligne 11409)
   - `run_test` (ligne 11417)
   - `display_test_results` (ligne 11431)
   - `display_quick_test_results` (ligne 11529)
   - `show_test_help` (ligne 11586)
   - `setup_ui` (ligne 11649)
   - `browse_folder` (ligne 11729)
   - `validate_and_save` (ligne 11741)
   - `_save_identified_environment` (ligne 11792)
   - `cancel` (ligne 11845)

### src\cy8_rag_manager.py
   - `_initialize_chromadb` (ligne 130)
   - `_initialize_embeddings_model` (ligne 175)
   - `_initialize_constraints_db` (ligne 204)
   - `_initialize_todo_manager` (ligne 259)
   - `_prepare_content_for_indexing` (ligne 411)
   - `_generate_document_id` (ligne 452)
   - `_update_error_history` (ligne 459)
   - `_update_server_state` (ligne 511)
   - `_query_rapid_mode` (ligne 776)
   - `_query_expert_mode` (ligne 807)
   - `_generate_template_response` (ligne 851)
   - `_prepare_context_for_mistral` (ligne 936)
   - `_call_mistral_for_analysis` (ligne 995)
   - `get_current_focus` (ligne 1287)
   - `get_current_focus` (ligne 1598)

### src\cy8_rag_tester.py
   - `environment_id` (ligne 25)
   - `_test_initial_state` (ligne 116)
   - `_test_temporal_search` (ligne 277)
   - `_test_error_memory` (ligne 323)
   - `_test_environment_consistency` (ligne 377)
   - `_generate_summary` (ligne 480)
   - `_save_test_results` (ligne 536)
   - `quick_learning_test` (ligne 557)

### src\cy8_temporal_rag.py
   - `test_temporal_rag` (ligne 183)

### src\cy8_test_suite.py
   - `setUp` (ligne 26)
   - `tearDown` (ligne 33)
   - `test_database_initialization` (ligne 46)
   - `test_prompt_crud_operations` (ligne 61)
   - `test_model_derivation` (ligne 126)
   - `test_no_repair_on_missing_table` (ligne 142)
   - `test_validate_database_structure_missing_table` (ligne 207)
   - `setUp` (ligne 244)
   - `tearDown` (ligne 250)
   - `test_full_system_initialization` (ligne 258)
   - `test_prompt_values_structure` (ligne 281)
   - `test_workflow_structure` (ligne 302)
   - `run_tests` (ligne 332)
   - `test_imports` (ligne 361)

### src\cy8_todo_manager.py
   - `_initialize_database` (ligne 29)
   - `get_current_focus` (ligne 228)
   - `format_todo_item` (ligne 359)

### src\cy8_user_preferences.py
   - `_get_preferences_directory` (ligne 30)
   - `_load_preferences` (ligne 46)
   - `_load_cookies` (ligne 63)
   - `_save_preferences` (ligne 75)
   - `_save_cookies` (ligne 87)
   - `_update_recent_databases` (ligne 108)
   - `get_cookie` (ligne 160)
   - `set_error_solutions_directory` (ligne 191)


## 📁 DÉTAIL PAR FICHIER
----------------------------------------------------------------------
### src\cy6_Queue.py
   📝 Lignes: 40
   ⚙️  Fonctions: 0
   🏗️  Classes: 1
   📦 Imports: 4

### src\cy6_file.py
   📝 Lignes: 20
   ⚙️  Fonctions: 3
   🏗️  Classes: 0
   📦 Imports: 1
   🔓 Fonctions publiques: load_json, save_json, log_json

### src\cy6_task_comfyui.py
   📝 Lignes: 52
   ⚙️  Fonctions: 4
   🏗️  Classes: 1
   📦 Imports: 5
   🔓 Fonctions publiques: update_values, log_values, addToQueue, GetImages

### src\cy6_websocket_api_client.py
   📝 Lignes: 421
   ⚙️  Fonctions: 15
   🏗️  Classes: 0
   📦 Imports: 9
   🔓 Fonctions publiques: socket_queue_prompt, get_image, get_history, get_queue_status, is_prompt_in_queue, socket_get_images, update_workflow, server_run_now, server_get_prompt, socket_queue_add
      ... et 5 autres

### src\cy6_wkf001_Basic.py
   📝 Lignes: 65
   ⚙️  Fonctions: 1
   🏗️  Classes: 1
   📦 Imports: 6
   🔓 Fonctions publiques: run_now

### src\cy8_comfyui_customNode_call.py
   📝 Lignes: 635
   ⚙️  Fonctions: 18
   🏗️  Classes: 1
   📦 Imports: 9
   🔓 Fonctions publiques: example_usage, get_custom_nodes_info, get_available_custom_node_types, create_custom_node_workflow, execute_custom_node_workflow, call_custom_node, test_extra_path_reader_direct, get_python_path_from_comfyui, get_extra_paths, get_custom_node_schema
      ... et 4 autres

### src\cy8_database_manager.py
   📝 Lignes: 1169
   ⚙️  Fonctions: 38
   🏗️  Classes: 1
   📦 Imports: 5
   🔓 Fonctions publiques: init_database, ensure_additional_columns, remove_legacy_image_column, add_default_basic_prompt, derive_model_from_workflow, get_all_prompts, get_prompt_by_id, update_prompt, create_prompt, delete_prompt
      ... et 27 autres

### src\cy8_editable_tables.py
   📝 Lignes: 845
   ⚙️  Fonctions: 33
   🏗️  Classes: 1
   📦 Imports: 5
   🔓 Fonctions publiques: edit_inputs_popup, create_prompt_values_table, create_workflow_table, load_prompt_values_data, load_workflow_data, on_values_double_click, on_workflow_double_click, edit_cell_inline, show_output_images, edit_multiloras
      ... et 21 autres

### src\cy8_fast_image_processor.py
   📝 Lignes: 174
   ⚙️  Fonctions: 10
   🏗️  Classes: 1
   📦 Imports: 7
   🔓 Fonctions publiques: get_image_processor, create_thumbnail_fast, get_image_dimensions_fast, calculate_image_hash_fast, create_thumbnail, get_dimensions, calculate_hash, get_performance_info

### src\cy8_image_index_manager.py
   📝 Lignes: 554
   ⚙️  Fonctions: 14
   🏗️  Classes: 1
   📦 Imports: 13
   🔓 Fonctions publiques: scan_directory, get_images, get_thumbnail, mark_deleted, restore_deleted, clear_cache, get_stats, close

### src\cy8_log_analyzer.py
   📝 Lignes: 544
   ⚙️  Fonctions: 20
   🏗️  Classes: 1
   📦 Imports: 5
   🔓 Fonctions publiques: test_log_analyzer, analyze_log_file, get_all_entries, get_summary_text

### src\cy8_mistral.py
   📝 Lignes: 246
   ⚙️  Fonctions: 5
   🏗️  Classes: 0
   📦 Imports: 6
   🔓 Fonctions publiques: get_mistral_answer, analyze_comfyui_error, save_error_solution, load_error_solution, analyze_comfyui_log_complete

### src\cy8_paths.py
   📝 Lignes: 258
   ⚙️  Fonctions: 26
   🏗️  Classes: 1
   📦 Imports: 3
   🔓 Fonctions publiques: get_default_db_path, normalize_path, ensure_dir, set_extra_paths, get_extra_path, get_all_extra_paths, set_extra_paths, get_extra_path_by_key, get_all_extra_paths, find_paths_containing
      ... et 15 autres

### src\cy8_popup_id_manager.py
   📝 Lignes: 108
   ⚙️  Fonctions: 11
   🏗️  Classes: 1
   📦 Imports: 2
   🔓 Fonctions publiques: get_popup_id, close_popup, get_next_id, register_popup, unregister_popup, get_active_popups, get_popup_history, format_title, print_status

### src\cy8_popup_manager.py
   📝 Lignes: 630
   ⚙️  Fonctions: 16
   🏗️  Classes: 1
   📦 Imports: 5
   🔓 Fonctions publiques: center_window, load_json_to_text, prompt_form, open_multi_loras_popup, show_output_images_popup, save_prompt, cancel, refresh_table, add_lora, edit_lora
      ... et 5 autres

### src\cy8_preferences_manager.py
   📝 Lignes: 143
   ⚙️  Fonctions: 6
   🏗️  Classes: 0
   📦 Imports: 5
   🔓 Fonctions publiques: show_info, clean_recent, clear_all, clear_recent_only, set_default_db, main

### src\cy8_prompts_manager_main.py
   📝 Lignes: 11858
   ⚙️  Fonctions: 257
   🏗️  Classes: 2
   📦 Imports: 109
   🔓 Fonctions publiques: center_window, main, restore_saved_environment, update_chat_welcome_message, add_startup_environment_message, add_no_environment_message, init_images_paths, setup_main_window, setup_ui, create_menu
      ... et 235 autres

### src\cy8_rag_manager.py
   📝 Lignes: 1629
   ⚙️  Fonctions: 33
   🏗️  Classes: 3
   📦 Imports: 18
   🔓 Fonctions publiques: main, add_constraint, get_constraints, index_analysis_result, search_similar_issues, get_server_status_summary, generate_chat_context, query_with_mode, get_mode_info, is_available
      ... et 8 autres

### src\cy8_rag_tester.py
   📝 Lignes: 610
   ⚙️  Fonctions: 14
   🏗️  Classes: 1
   📦 Imports: 6
   🔓 Fonctions publiques: environment_id, run_quick_test, run_complete_test_suite, quick_learning_test

### src\cy8_temporal_rag.py
   📝 Lignes: 278
   ⚙️  Fonctions: 5
   🏗️  Classes: 1
   📦 Imports: 7
   🔓 Fonctions publiques: test_temporal_rag, search_with_temporal_priority, search_recent_only, get_temporal_distribution

### src\cy8_test_suite.py
   📝 Lignes: 408
   ⚙️  Fonctions: 14
   🏗️  Classes: 3
   📦 Imports: 12
   🔓 Fonctions publiques: run_tests, test_imports, setUp, tearDown, test_database_initialization, test_prompt_crud_operations, test_model_derivation, test_no_repair_on_missing_table, test_validate_database_structure_missing_table, setUp
      ... et 4 autres

### src\cy8_todo_manager.py
   📝 Lignes: 387
   ⚙️  Fonctions: 13
   🏗️  Classes: 1
   📦 Imports: 7
   🔓 Fonctions publiques: add_todo, get_todos, start_focus, end_focus, get_current_focus, get_todo_by_id, update_todo_status, restore_chat_history, get_focus_context, format_todos_list
      ... et 1 autres

### src\cy8_user_preferences.py
   📝 Lignes: 211
   ⚙️  Fonctions: 21
   🏗️  Classes: 1
   📦 Imports: 5
   🔓 Fonctions publiques: get_last_database_path, set_last_database_path, get_recent_databases, get_window_geometry, set_window_geometry, get_preference, set_preference, get_cookie, set_cookie, clear_recent_databases
      ... et 4 autres
