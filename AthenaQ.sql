SELECT 
  userid,
  COUNT(DISTINCT act_date) AS active_days,
  
  -- Chat interactions
  SUM(chat_aicodelines) AS total_chat_aicodelines,
  SUM(chat_messagesinteracted) AS total_chat_messagesinteracted,
  SUM(chat_messagessent) AS total_chat_messagessent,
  
  -- Code fix metrics
  SUM(codefix_acceptanceeventcount) AS total_codefix_acceptanceeventcount,
  SUM(codefix_acceptedlines) AS total_codefix_acceptedlines,
  SUM(codefix_generatedlines) AS total_codefix_generatedlines,
  SUM(codefix_generationeventcount) AS total_codefix_generationeventcount,
  
  -- Code review metrics
  SUM(codereview_failedeventcount) AS total_codereview_failedeventcount,
  SUM(codereview_findingscount) AS total_codereview_findingscount,
  SUM(codereview_succeededeventcount) AS total_codereview_succeededeventcount,
  
  -- Dev metrics
  SUM(dev_acceptanceeventcount) AS total_dev_acceptanceeventcount,
  SUM(dev_acceptedlines) AS total_dev_acceptedlines,
  SUM(dev_generatedlines) AS total_dev_generatedlines,
  SUM(dev_generationeventcount) AS total_dev_generationeventcount,
  
  -- Doc generation metrics
  SUM(docgeneration_eventcount) AS total_docgeneration_eventcount,
  SUM(docgeneration_acceptedfileupdates + docgeneration_acceptedfilescreations) AS total_docgeneration_acceptedfiles,
  SUM(docgeneration_acceptedlineadditions + docgeneration_acceptedlineupdates) AS total_docgeneration_acceptedlines,
  SUM(docgeneration_rejectedfilecreations + docgeneration_rejectedfileupdates) AS total_docgeneration_rejectedfiles,
  SUM(docgeneration_rejectedlineadditions + docgeneration_rejectedlineupdates) AS total_docgeneration_rejectedlines,
  
  -- Inline chat metrics
  SUM(inlinechat_eventcount) AS total_inlinechat_eventcount,
  SUM(inlinechat_acceptedlineadditions + inlinechat_acceptedlinedeletions) AS total_inlinechat_acceptedlines,
  SUM(inlinechat_rejectedlineadditions + inlinechat_rejectedlinedeletions) AS total_inlinechat_rejectedlines,
  SUM(inline_aicodelines) AS total_inline_aicodelines,
  SUM(inline_acceptancecount) AS total_inline_acceptancecount,
  SUM(inline_suggestionscount) AS total_inline_suggestionscount,
  
  -- Test generation metrics
  SUM(testgeneration_eventcount) AS total_testgeneration_eventcount,
  SUM(testgeneration_acceptedlines) AS total_testgeneration_acceptedlines,
  SUM(testgeneration_acceptedtests) AS total_testgeneration_acceptedtests,
  SUM(testgeneration_generatedlines) AS total_testgeneration_generatedlines,
  SUM(testgeneration_generatedtests) AS total_testgeneration_generatedtests,
  
  -- Transformation metrics
  SUM(transformation_eventcount) AS total_transformation_eventcount,
  SUM(transformation_linesgenerated) AS total_transformation_linesgenerated,
  SUM(transformation_linesingested) AS total_transformation_linesingested,
  
  -- Derived metrics
  SUM(codefix_acceptedlines) / NULLIF(SUM(codefix_generatedlines), 0) AS codefix_acceptance_ratio,
  SUM(dev_acceptedlines) / NULLIF(SUM(dev_generatedlines), 0) AS dev_acceptance_ratio,
  SUM(testgeneration_acceptedtests) / NULLIF(SUM(testgeneration_generatedtests), 0) AS test_acceptance_ratio
  
FROM devq_userdata_stats
GROUP BY userid
ORDER BY COUNT(DISTINCT act_date) DESC;
