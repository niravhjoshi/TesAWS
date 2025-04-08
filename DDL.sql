CREATE EXTERNAL TABLE `devq_userdata_stats`(
  `userid` string, 
  `act_date` string, 
  `chat_aicodelines` int, 
  `chat_messagesinteracted` int, 
  `chat_messagessent` int, 
  `codefix_acceptanceeventcount` int, 
  `codefix_acceptedlines` int, 
  `codefix_generatedlines` int, 
  `codefix_generationeventcount` int, 
  `codereview_failedeventcount` int, 
  `codereview_findingscount` int, 
  `codereview_succeededeventcount` int, 
  `dev_acceptanceeventcount` int, 
  `dev_acceptedlines` int, 
  `dev_generatedlines` int, 
  `dev_generationeventcount` int, 
  `docgeneration_acceptedfileupdates` int, 
  `docgeneration_acceptedfilescreations` int, 
  `docgeneration_acceptedlineadditions` int, 
  `docgeneration_acceptedlineupdates` int, 
  `docgeneration_eventcount` int, 
  `docgeneration_rejectedfilecreations` int, 
  `docgeneration_rejectedfileupdates` int, 
  `docgeneration_rejectedlineadditions` int, 
  `docgeneration_rejectedlineupdates` int, 
  `inlinechat_acceptedlineadditions` int, 
  `inlinechat_acceptedlinedeletions` int, 
  `inlinechat_eventcount` int, 
  `inlinechat_rejectedlineadditions` int, 
  `inlinechat_rejectedlinedeletions` int, 
  `inline_aicodelines` int, 
  `inline_acceptancecount` int, 
  `inline_suggestionscount` int, 
  `testgeneration_acceptedlines` int, 
  `testgeneration_acceptedtests` int, 
  `testgeneration_eventcount` int, 
  `testgeneration_generatedlines` int, 
  `testgeneration_generatedtests` int, 
  `transformation_eventcount` int, 
  `transformation_linesgenerated` int, 
  `transformation_linesingested` int)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://awss3-awsdevq-promptlog/devqpromptlog/AWSLogs/985539799335/QDeveloperLogs/by_user_analytic/us-east-1'
TBLPROPERTIES (
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1742984936')
