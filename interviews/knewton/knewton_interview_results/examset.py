import random
import math


class QuestionResult:
    """Class for storing the result of a question. Used when reading in data."""
    def __init__(self, question_id, student_id, correct):
        self.question_id = question_id  
        self.student_id = student_id
        self.correct = correct

class StudentResult:
    """Class for storing the result of a particular student's performance on 
       test exams. Created and populated when reading in data an processing it."""
    def __init__(self, question_results, student_id, num_correct, num_questions):
        self.question_results = question_results  # hash of question_id : QuestionResult
        self.student_id = student_id
        self.num_correct = num_correct
        self.num_questions = num_questions
        self.theta = 0

    def percentage_correct():
        return self.num_correct*1.0 / self.num_questions

class Question:
    """Class for one of the questions asked. Methods provide a question_id, 
       a probability of getting the question right, and the entropy."""
    def __init__(self, question_id, rj):
        self.question_id = question_id
        self.rj = rj
        self.entropy = get_entropy(self.rj) + get_entropy(1 - self.rj) 

class Student:
    """Potential student. This is a model of a random student taking a set of
       k questions. Used when creating an ExamSet and evaluating the set."""
    def __init__(self, questions):
        self.questions = questions # hash of question_id : Question
        self.k = len(self.questions)
        self.score_probabilities = None

    def get_score_dispersion(self):
        """Returns the max_score - min_score (range of the score possibilities."""
        self.get_score_probabilities()
        max_score = None
        min_score = None
        for score, prob in self.score_probabilities:
            if max_score == None or score > max_score:
                max_score = score
            if min_score == None or score < min_score:
                min_score = score
        return max_score - min_score

    def get_score_probabilities(self):
        """Returns a list of tuples of (score, probability) for all of the 
           possible combinations of scores and their probabilities for a given
           student."""
        if not self.score_probabilities:
            self.score_probabilities = self._exponential_recursion(0, [(0,1)])
        return self.score_probabilities

    def _exponential_recursion(self, i, score_prob):
        # method for getting the score probabilities by doing all possible 
        # combinations of scores. 
        current_rj = self.questions[i].rj 
        new_score_prob = []
        for score, prob in score_prob:
            # create new tuples based on each of the previous scores.
            new_score = score + 1.0/current_rj
            incorrect = (score, prob*abs(1.0-current_rj))
            correct = (new_score, prob*1.0*current_rj)
            new_score_prob.append(incorrect)
            new_score_prob.append(correct)
        # recurse until we run out of questions
        if i+1 < len(self.questions):
            return self._exponential_recursion(i+1, new_score_prob)
        else:
            return new_score_prob

    def get_score_probabilities_approx(self):
        """Gets an approximation for the score probabilities, unless the 
           score probabilities are already computed."""
        if self.score_probabilities:
            return self.score_probabilities
        probs = [1] + [0 for x in xrange(self.k-1)]
        for q in xrange(1,self.k+1,1):
            new_probs = []
            for s in xrange(self.k+1):
                if s > q:
                    # if score is greater than q, no possible way to get that score
                    new_probs.append(0.0)
                else:
                    extra_term = 0
                    # recursive formula for new probability
                    if s-1 >= 0:
                        extra_term = probs[s-1]*self.questions[q].rj
                    new_probs.append(extra_term + probs[s]*(1.0-self.questions[q].rj))
            probs = new_probs
        self.score_probabilities = probs
        return probs

class ProbabilisticQuestionSet:
    """This class takes as input a list of questions and allows one to select 
       a question at random according to the entropies. The probability of
       choosing a question is a function of the max and minimum entropy, some
       parameter c for making the number of trials a constant, and the current 
       questions entropy. See the writeup for more details.
    """
    def __init__(self, questions, c=200.0):
        self.question_list = questions
        self.probability_bins = self._get_probability_bins(c)
 
    def _get_probability_bins(self, c):
        # find the minimum and maximum entropies
        old_entropy_list = [question.entropy for question in self.question_list]
        min_entropy = min(old_entropy_list)
        max_entropy = max(old_entropy_list)

        # compute the new entropies H' which take into account the
        # factor that corrects for very small entropies. 
        scaling_factor = float(max_entropy - min_entropy)/(c-1)
        new_entropies = [question.entropy + scaling_factor for question in self.question_list]
        total_new_entropy = sum(new_entropies)
        
        # make these new entropies into probabilities and build the buckets
        probabilities = [float(entropy)/total_new_entropy for entropy in new_entropies]     
        bins = []
        previous = 0
        for i in xrange(len(probabilities)):
            bins.append(probabilities[i] + previous)
            previous = bins[i]

        return bins

    def sample(self, n, already_used = {}):
        """Provides a sample of n questions with no repeats."""
        result = []

        # Las Vegas algorithm that repeatedly samples until we are done,
        # throwing away samples that we have already used.
        # Note that this assumes that n is much smaller than the number of
        # questions available.
        while len(already_used) < n:
            index = self.bin_search(random.random())
            if index not in already_used:
                result.append(self.question_list[index])
                already_used[index] = self.question_list[index]
        return result

    def bin_search(self, rand):
        index = self._binary_search_bins(0, len(self.probability_bins)-1, rand)
        # check if rand is on the left or the right
        if index == 0 or index == len(self.probability_bins)-1:
            return index

        # we want to get the index where rand is less than the value
        # i.e. if we have rand = 0.85 and bins [0.5, 1], then we want
        # to return bin of index 0. However if we have rand = 0.2, we also
        # want to return index 0.
        if self.probability_bins[index] > rand:
            return index - 1
        else:
            return index
     
    def _binary_search_bins(self, low, high, value):
        """Performs a binary search for the index or closest index
           to value, plus or minus one index."""
        if high <= low:
            return low 
        mid = (low + high)/2
        mid_value = self.probability_bins[mid] 
        if value < mid_value:
            return self._binary_search_bins(low, mid-1, value)
        elif value > mid_value:
            return self._binary_search_bins(mid+1, high, value)
        else:
            return mid         


class ExamSet:
    """Class which represents an possible ExamSet to be given to a set of 
       students. The ExamSet contains a list of students and the possible 
       questions that will be posed.

       NOTE: ExamSet has a rep invariant that the student_list is final. The
       behavior of this class when self.students is changed is unspecified. 

    """
    def __init__(self, student_list, bin_size=None):
        self.students = student_list
        self.entropy = None
        self.bins = None
        self.num_distinct_questions = None
        if bin_size:
            self.bin_size = bin_size
        else:
            self.bin_size = self.compute_bin_size(student_list)


    def get_num_distinct_questions(self):
        """Gets the number of distinct questions that exist for this ExamSet."""
        if self.num_distinct_questions:
            return self.num_distinct_questions
        if self.students:
            question_ids = {}
            # iterate over each student, and each question for each student, and
            # add these to our hash of question_ids
            for student in self.students:
                for question in student.questions:
                    question_ids[question.question_id] = True
            self.num_distinct_questions = len(question_ids)
        else:
            self.num_distinct_questions = 0
        return self.num_distinct_questions
        

    def compute_bin_size(self, students):
        """Computes the bin size to use for computing entropies and 
           probabilities."""
        max_disp = None
        min_disp = None
        for student in students:
            disp = student.get_score_dispersion()
            if max_disp == None or disp > max_disp:
                max_disp = disp
            if min_disp == None or disp < max_disp:
                min_disp = disp
        # current heuristic is to take the minimum score dispersion and multiply by 2.5
        # we would rather have small bin size, then bins which are too large.
        self.bin_size = min_disp * 0.75
        return self.bin_size

    def compute_entropy(self):
        """Computes the entropy of the examset."""
        if self.entropy:
            return self.entropy
        if not self.bins:
            self.bins = self.build_histogram(self.bin_size)
        entropy = 0
        for cumulative_prob, count in self.bins.itervalues():
            avg_prob = cumulative_prob * 1.0 / count
            entropy += get_entropy(avg_prob)
        self.entropy = entropy
        return entropy

    def build_histogram(self, bin_size):
        """Returns a dictionary where keys are the bin, and the values
           are an array of the total cumulative probability prob and the count
           so that we have [prob, count]."""
        bins = {}
        # bins that give the total cumulative probability, and count of 
        # the number of occurrences
        for student in self.students:
            score_probabilities = student.get_score_probabilities()
            for (score, prob) in score_probabilities:
                current_bin = score // bin_size
                if current_bin in bins:
                    bins[current_bin][0] += prob
                    bins[current_bin][1] += 1 
                else:
                    bins[current_bin] = [prob, 1]
        return bins
  
    def mutate(self, rate, probabilistic_question_set_object):
        """Returns a new examset with a mutated copy of all the variables.
           The new examset is separate from the current one, so that changing properties
           in the mutated examset does not change anything in current ExamSet.
        """
        student_list = self.students[:] # shallow copy of the entire list
        for student in student_list:
            new_mutations = False
            updated_questions = {}
            for i in xrange(len(student.questions)):
                # delete questions from student.questions at random, according
                # to some mutation rate.
                if random.random() < rate:
                    new_mutations = True
                else:
                    updated_questions[student.questions[i].question_id] = student.questions[i]
            if new_mutations:
                # mutate the current sample so that we obtain student.k questions for this student
                student.questions = probabilistic_question_set_object.sample(student.k, updated_questions)

        return ExamSet(student_list, self.bin_size)

    def crossover(self, examset, rate=0.5):
        """Returns a new examset which is a crossover of the current examset and the
           ExamSet passed in as an argument. The crossovers occur with probability given
           by the crossover rate parameter.
        """ 
        student_list = self.students[:] # shallow copy of the entire list
        for i in xrange(len(student_list)):
            # randomly choose whether or not to cross over this student's 
            # list of questions with the other examset's list.
            if random.random() < rate:
                # exchange the current list of questions with the list of
                # questions that are used by the other examset
                student_list[i].questions = examset.students[i].questions

        # average out the bin size and create a new ExamSet 
        return ExamSet(student_list, float(self.bin_size + examset.bin_size)/2)
       
 
class ComputeProbabilities:
    """Class for reading in the question results and creating students."""
    def __init__(self, question_results, min_threshold_change=0.05, max_num_iterations=250):
        self.question_results = question_results
        self.min_threshold_change = min_threshold_change
        self.max_num_iterations = max_num_iterations

        # create student_result objects and group them by question for easier usage
        self.student_results = self._create_students() # hash of student_id : StudentResult object
        self.questions_students_dict = self._create_questions_students_dict() # hash of question_id : [StudentResult] 

        # hash of question_id : Question where the Questions have rj computed 
        self.questions = self.compute_rj(self)
        # questions sorted by entropies, highest first.
        self.sorted_questions = None 

    def _create_students(self):
        students = {}

        # students is a hash that stores a student id as a key and contains 
        # a StudentResult object
        for question in self.question_results:
            if question.student_id in students:
                # if studentResult for the id is already in the hash, change it.
                students[question.student_id].question_results[question.question_id] = question
                students[question.student_id].num_questions += 1
                if question.correct:
                    students[question.student_id].num_correct += 1
            else:
                # if the student id is not in the hash, create a new StudentResult object and add it
                if question.correct:
                    num_correct = 1
                else:
                    num_correct = 0
                stud_result = StudentResult({question.question_id : question}, question.student_id, num_correct, 1)
                students[question.student_id] = stud_result
        return students

    def get_top_questions(self, n):
        """Gets the n questions with the highest entropy, note that this method
           mutates the ordering of the questions in self.questions. After this
           method is called, the questions will be ordered by highest entropy
           first.
        """
        if self.sorted_questions:
            return self.sorted_questions[:n]
        self.sorted_questions = sorted(self.questions.values(), key = lambda q : q.entropy, reverse=True)
        return self.sorted_questions[:n]

    def _create_questions_students_dict(self):
        # creates a dictionary of all the questions, with the value of the dictionary 
        # being all of the students who were given that question in the training data.
        qs_dict = {}
        for student_id, student_result in self.student_results.iteritems():
            for question_result in student_result.question_results.itervalues():
                # check if the question_id is already in the dictionary
                # and add the student id to the list accordingly
                if question_result.question_id in qs_dict:
                    qs_dict[question_result.question_id].append(student_result)
                else:
                    qs_dict[question_result.question_id] = [student_result]
        return qs_dict

    def compute_rj_uar_assumption(self):
        """Method which just takes the sample means, and uses these as the probabilities of getting
           a question correct."""
        question_list = {}
        for question_id, students_list in self.questions_students_dict.iteritems():
            count = 0
            correct = 0
            for student in students_list:
                correct += student.question_results[question_id].correct
                count += 1
            rj = correct * 1.0 / count
            question = Question(question_id, rj)
            # add the question to the question_list hash
            question_list[question_id] = question
        return question_list 

    def continue_iteration(self, iteration, distance_change):
        """Computes whether or not we should continue the current iteration
           in the algorithm that iteratively computes rj. The min_threshold_change
           and max_num_iterations will be computed using the first couple of 
           iterations as a guide."""
        if iteration <= 0:
            return True
        if distance_change < self.min_threshold_change or iteration > self.max_num_iterations:
            return False
        return True

    def compute_rj(self, delta):
        """Method which iteratively computes the probability of a given question begin asked."""
        # initialize weights by using the uar assumption, and begin to iterate
        questions = self.compute_rj_uar_assumption()
        
        # iterate over the students, and each one of the questions that they answered
        # reassigning the theta_i's when necessary
        iteration = 0
        distance_change = None
        while self.continue_iteration(iteration, distance_change):
            delta = 0.5 * math.exp(-(iteration+1))
            additional_delta_vec = [-delta, 0, delta]
            print "  Computing r_j and theta_i; iteration %s" % str(iteration)

            # first part of the iteration: change thetas for all the students
            distance_change = self._iteratively_compute_rj_or_theta_i(self.student_results, additional_delta_vec, questions, "student")
            # second part of the iteration: change rjs for all the questions
            distance_change += self._iteratively_compute_rj_or_theta_i(self.questions_students_dict, additional_delta_vec, questions, "question")
       
            iteration += 1
        return questions

    def _iteratively_compute_rj_or_theta_i(self, iteration_dictionary, additional_delta_vec, questions, toplevel="question"):        
        total_distance_change = 0
        for key, value in iteration_dictionary.iteritems():
            # distance is initialized as zero and increases as we get farther away from
            # the correct answer. The ordering of the inputs to distance are given by
            # [current_rj + theta_i - delta, current_rj + theta_i, current_rj + theta_i + delta]
            distance = [0, 0, 0]

            # if we're calling on question, then the question_id is given by key, otherwise 
            # the student_id is given by the key.
            if toplevel == "question":                
                question = questions[key]
                secondary_list = value # list of [StudentResult] Objects
            else:
                student = value
                secondary_list = value.question_results.values() # list of [QuestionResult] Objects

            # iterate over the secondary_list and calculate the min distance
            for secondary_item in secondary_list:
                # if we're calling on question, then the student is the secondary_item in the list, otherwise
                # we're calling on student, which means the question_result is the secondary_item in the list
                if toplevel == "question":
                    question_result = secondary_item.question_results[key]
                    student = secondary_item
                else:
                    question_result = secondary_item
                    question = questions[secondary_item.question_id]

                xij = (1 if question_result.correct else 0) 
                added_distance = [abs(xij - (question.rj + student.theta + i)) for i in additional_delta_vec]  
                
                # add the added_distance to the current distance to get a new measure for the 
                # distance, given this new question
                for i in xrange(len(distance)):
                    distance[i] += added_distance[i]

            # now we have a distance vector which gives us the min distance for [rj+thetai-delta, rj+thetai, rj+thetai+delta]
            # and we can evaluate which one is the best, and choose that one as the new theta_i or rj.
            best_index = distance.index(min(distance))
            total_distance_change += (distance[1] - min(distance))

            # update rj if we're calling on questions and theta_i if we're calling on students
            if toplevel == "question":
                question.rj += additional_delta_vec[best_index]
                question.rj = self._constrain_to_zero_one(question.rj)
            else:
                student.theta += additional_delta_vec[best_index]
                student.theta = self._constrain_to_zero_one(student.theta)
        return total_distance_change

    def _constrain_to_zero_one(self, prob):
        if prob < 0:
            return 0
        if prob > 1:
            return 1
        return prob


class QuestionAssignment:
    """Class which creates an ExamSet satisfying the conditions specified in our problem.
       The num_students parameter tells us how many students there should be in the 
       resulting ExamSet, and the num_questions_per_student parameter tells us how 
       many questions there should be per student. 

       There are two methods for question_assignment -- One uses a randomized greedy 
       algorithm and can be called with greedy_assignment(), and the other uses a 
       genetic algorithm and can be called with genetic_assignment().
    """
    def __init__(self, question_results, num_students, num_questions_per_student, total_required_questions):
        self.question_results = question_results
        self.num_students = num_students
        self.num_questions_per_student = num_questions_per_student 
        self.total_required_questions = total_required_questions

        # we initialize a compute probabilities object which will compute rj for all of the questions
        self.compute_probabilities = ComputeProbabilities(question_results)

    def get_probabilistic_question_set_all_questions(self):
        return ProbabilisticQuestionSet(self.compute_probabilities.questions.values())

    def greedy_assignment(self):
        # get the top L=self.total_required_questions number of questions, and insert them into an examset 
        # with probability proportional to their entropy.
        top_questions = self.compute_probabilities.get_top_questions(self.total_required_questions)
        top_questions_set = ProbabilisticQuestionSet(top_questions)
        newExamSet = None 

        # we continue looping until we've reached the requisite number of questions
        counter = 0
        while newExamSet == None or newExamSet.get_num_distinct_questions < self.total_required_questions:
            print "  Greedy Assignment: beginning iteration %s" % (str(counter))
            student_list = []
            for i in xrange(self.num_students):
                # create a new student with num_questions_per_student randomly sampled questions
                current_student_questions = top_questions_set.sample(self.num_questions_per_student, {})
               
                # create a student and append him to the list
                student_list.append(Student(current_student_questions))
            newExamSet = ExamSet(student_list)
            counter += 1
            print "  Greedy Assignment: finished iteration %s" % (str(counter-1))
        return newExamSet
                
def get_entropy(rj):
    if rj == 0:
        return 0
    return rj*math.log(1.0/rj)
