בהינתן אישיו נקבל את כל מימושים והטסטים שנדרשנו לכתוב כדי לספק את האילוץ

SELECT M.*, F.Path, F.FileType --all methods of the commit
FROM CommitFiles as F, CommitChanges as C, MethodData as M
WHERE F.CommitID in (
	SELECT CommitID --all commits relevant to the issue
	FROM CommitsIssuesLinkage 
	WHERE IssueID = 'issue_id')
AND (C.OldPath = F.Path OR C.NewPath = F.Path)
AND F.CommitID = C.CommitID
AND M.CommitID = C.CommitID AND M.MethodName = C.MethodName


קישור אישיואים שקשורים אחד לשני עי מתודה:
בהינתן אישיו פיצר נקבל את הבאגים שלו

SELECT * FROM JiraIssues
WHERE IssueType = 'Bug'
AND IssueID in ( 
	SELECT IssueID FROM CommitsIssuesLinkage
	WHERE CommitID in (
		SELECT Distinct CommitID FROM CommitChanges --all commits relevant to the methods below
		WHERE MethodName in (
			SELECT Distinct MethodName FROM CommitChanges --all methods relevant to the commits below
			WHERE CommitID in (
				SELECT CommitID --all commits relevant to the issue
				FROM CommitsIssuesLinkage 
				WHERE IssueID = 'issue_id'))))
ORDER BY Date;


בהינתן שם של מתודה כל הדרישות שרלוונטיות ל מתודה הזאת מסודרות לפי זמן
SELECT * FROM JiraIssues
WHERE IssueID in (
	SELECT IssueID FROM CommitsIssuesLinkage --all issues connected to the commits below
	WHERE CommitID in (
		SELECT Distinct CommitID --all commits relevant to the method
		FROM CommitChanges
		WHERE MethodName = 'method_name'))
ORDER BY Date;


בהינתן שם של מתודה כל הטסטים שרלוונטיים למתודה הזאת
SELECT Date, M.* FROM MethodData as M, Commits --all method data of the methods below
WHERE (M.CommitID, MethodName) in (
	SELECT Distinct CommitID, MethodName FROM ( -- all the method in the test paths below
		SELECT CommitID, MethodName, NewPath as Path 
		FROM CommitChanges
		UNION
		SELECT CommitID, MethodName, OldPath as Path
		FROM CommitChanges)
	WHERE  (CommitID, Path) in (
		SELECT CommitID, Path --all the test files int the commits below
		FROM CommitFiles
		WHERE FileType = 'TEST'
		AND CommitID in (
			SELECT Distinct CommitID --all commits relevant to the method
			FROM CommitChanges
			WHERE MethodName = 'method_name')))
AND Commits.CommitID = M.CommitID
ORDER BY Date, M.CommitID, MethodName,OldNew, LineNumber;		


