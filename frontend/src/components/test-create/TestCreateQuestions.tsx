import { useState, useEffect } from "react";
import { useTestStore, MCQQuestion, CodingQuestion } from "@/store/testStore";
import { apiClient } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Search, Plus, X, Check } from "lucide-react";

export function TestCreateQuestions() {
  const {
    testCreation,
    addMCQQuestion,
    removeMCQQuestion,
    addCodingQuestion,
    removeCodingQuestion,
  } = useTestStore();
  const [mcqSearch, setMcqSearch] = useState("");
  const [codingSearch, setCodingSearch] = useState("");

  const selectedMCQIds = testCreation.mcqQuestionIds || [];
  const selectedCodingIds = testCreation.codingQuestionIds || [];

  const [bankMCQs, setBankMCQs] = useState<MCQQuestion[]>([]);
  const [bankCoding, setBankCoding] = useState<CodingQuestion[]>([]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        // Try to fetch MCQ bank via filter endpoint (no filters = all)
        const mcqResp: any = await apiClient.filterMCQs({ language: '', difficulty_level: '' }).catch(() => null);
        const codingResp: any = await apiClient.filterCodingQuestions({}).catch(() => null);

        if (mounted) {
          const mcqs = Array.isArray(mcqResp?.data || mcqResp) ? (mcqResp.data || mcqResp) : [];
          const codings = Array.isArray(codingResp?.data || codingResp) ? (codingResp.data || codingResp) : [];

          // Normalize shapes for the component (id, question/title, tags, points, difficulty, language)
          setBankMCQs(
            mcqs.map((q: any) => ({
              id: q.question_id || q.id,
              question: q.question_text || q.question || q.text || '',
              tags: q.tags || [],
              points: q.marks || q.points || 0,
              difficulty: q.difficulty || q.difficulty_level || 'easy',
            }))
          );

          setBankCoding(
            codings.map((q: any) => ({
              id: q.question_id || q.id,
              title: q.title || q.problem_statement || q.name || '',
              description: q.description || q.problem_statement || '',
              tags: q.tags || [],
              points: q.marks || q.points || 0,
              difficulty: q.difficulty || 'easy',
              language: q.language || 'javascript',
              starterCode: q.starter_code || q.starterCode || '',
              testCases: q.test_cases || q.testCases || [],
            }))
          );
        }
      } catch (e) {
        // ignore - keep empty bank
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const filteredMCQs = bankMCQs.filter(
    (q) =>
      q.question.toLowerCase().includes(mcqSearch.toLowerCase()) ||
      (q.tags || []).some((t) => t.toLowerCase().includes(mcqSearch.toLowerCase()))
  );

  const filteredCoding = bankCoding.filter(
    (q) =>
      q.title.toLowerCase().includes(codingSearch.toLowerCase()) ||
      (q.tags || []).some((t) => t.toLowerCase().includes(codingSearch.toLowerCase()))
  );

  const toggleMCQ = (question: MCQQuestion) => {
    const qid = question.id || (question as any).question_id;
    if (selectedMCQIds.includes(qid)) {
      removeMCQQuestion(qid);
    } else {
      addMCQQuestion(qid);
    }
  };

  const toggleCoding = (question: CodingQuestion) => {
    const qid = question.id || (question as any).question_id;
    if (selectedCodingIds.includes(qid)) {
      removeCodingQuestion(qid);
    } else {
      addCodingQuestion(qid);
    }
  };

  // Compute total points from selected IDs using bank lists
  const totalPoints = [
    ...selectedMCQIds.map((id) => bankMCQs.find((b) => b.id === id)?.points || 0),
    ...selectedCodingIds.map((id) => bankCoding.find((b) => b.id === id)?.points || 0),
  ].reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="flex items-center gap-4 rounded-lg bg-accent/50 p-4">
        <div>
          <span className="text-sm text-muted-foreground">Selected:</span>
          <span className="ml-2 font-semibold">
            {testCreation.selectedMCQs.length} MCQs, {testCreation.selectedCoding.length} Coding
          </span>
        </div>
        <div className="h-4 w-px bg-border" />
        <div>
          <span className="text-sm text-muted-foreground">Total Points:</span>
          <span className="ml-2 font-semibold">{totalPoints}</span>
        </div>
      </div>

      <Tabs defaultValue="mcq" className="space-y-4">
        <TabsList>
          <TabsTrigger value="mcq">
            MCQ Questions ({testCreation.selectedMCQs.length})
          </TabsTrigger>
          <TabsTrigger value="coding">
            Coding Questions ({testCreation.selectedCoding.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="mcq">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">MCQ Question Bank</CardTitle>
              <CardDescription>Select questions to add to your test</CardDescription>
              <div className="relative mt-2">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search MCQ questions..."
                  value={mcqSearch}
                  onChange={(e) => setMcqSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12"></TableHead>
                    <TableHead>Question</TableHead>
                    <TableHead>Difficulty</TableHead>
                    <TableHead>Tags</TableHead>
                    <TableHead>Points</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredMCQs.map((q) => {
                    const isSelected = selectedMCQIds.includes(q.id);
                    return (
                      <TableRow
                        key={q.id}
                        className={isSelected ? "bg-accent/50" : "cursor-pointer hover:bg-muted/50"}
                        onClick={() => toggleMCQ(q)}
                      >
                        <TableCell>
                          <Button
                            variant={isSelected ? "default" : "outline"}
                            size="icon"
                            className="h-8 w-8"
                          >
                            {isSelected ? <Check className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                          </Button>
                        </TableCell>
                        <TableCell className="max-w-sm">
                          <p className="truncate">{q.question}</p>
                        </TableCell>
                        <TableCell>
                          <Badge variant={q.difficulty}>{q.difficulty}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            {q.tags.slice(0, 2).map((tag) => (
                              <Badge key={tag} variant="outline" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        </TableCell>
                        <TableCell>{q.points}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="coding">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Coding Question Bank</CardTitle>
              <CardDescription>Select coding challenges for your test</CardDescription>
              <div className="relative mt-2">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search coding questions..."
                  value={codingSearch}
                  onChange={(e) => setCodingSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12"></TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Difficulty</TableHead>
                    <TableHead>Language</TableHead>
                    <TableHead>Points</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredCoding.map((q) => {
                    const isSelected = selectedCodingIds.includes(q.id);
                    return (
                      <TableRow
                        key={q.id}
                        className={isSelected ? "bg-accent/50" : "cursor-pointer hover:bg-muted/50"}
                        onClick={() => toggleCoding(q)}
                      >
                        <TableCell>
                          <Button
                            variant={isSelected ? "default" : "outline"}
                            size="icon"
                            className="h-8 w-8"
                          >
                            {isSelected ? <Check className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                          </Button>
                        </TableCell>
                        <TableCell>
                          <p className="font-medium">{q.title}</p>
                          <p className="text-xs text-muted-foreground truncate max-w-xs">
                            {q.description.slice(0, 80)}...
                          </p>
                        </TableCell>
                        <TableCell>
                          <Badge variant={q.difficulty}>{q.difficulty}</Badge>
                        </TableCell>
                        <TableCell>{q.language}</TableCell>
                        <TableCell>{q.points}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Selected Questions Summary */}
      {(testCreation.selectedMCQs.length > 0 || testCreation.selectedCoding.length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Selected Questions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {selectedMCQIds.map((id) => {
                const q = bankMCQs.find((b) => b.id === id);
                return (
                  <Badge key={id} variant="secondary" className="gap-1 py-1">
                    MCQ: {q ? (q.question || '').slice(0, 30) : id}...
                    <button onClick={() => removeMCQQuestion(id)} className="ml-1 hover:text-destructive">
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                );
              })}
              {testCreation.selectedCoding.map((q) => (
                <Badge key={q.id} variant="secondary" className="gap-1 py-1">
                  Code: {q.title}
                  <button onClick={() => removeCodingQuestion(q.id)} className="ml-1 hover:text-destructive">
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
