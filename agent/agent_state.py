class AgentState:

    def __init__(self, goal, plan=None):

        self.goal = goal
        self.plan = plan or []

        self.current_step = 0

        self.completed_steps = []

        self.results = []

        self.status = "created"

        self.retry_count = 0

        # Normal retry limit
        self.max_retries = 2

        # Maximum number of retries that can be
        # triggered specifically by learned recovery.
        #
        # This is deliberately separate from the
        # normal retry mechanism.
        self.learned_retry_count = 0
        self.max_learned_retries = 1

        self.error = None


    # =====================================================
    # START
    # =====================================================

    def start(self):

        self.status = "running"


    # =====================================================
    # COMPLETE STEP
    # =====================================================

    def complete_step(
        self,
        step,
        result
    ):

        self.completed_steps.append(
            step
        )

        self.results.append(
            result
        )

        self.current_step += 1

        self.retry_count = 0

        self.learned_retry_count = 0

        self.error = None

        self.status = "running"


    # =====================================================
    # FINISH
    # =====================================================

    def finish(self):

        self.status = "completed"


    # =====================================================
    # FAIL
    # =====================================================

    def fail(self, error):

        self.status = "failed"

        self.error = error


    # =====================================================
    # NORMAL RETRY
    # =====================================================

    def retry(self):

        if self.retry_count < self.max_retries:

            self.retry_count += 1

            self.status = "retrying"

            return True

        self.status = "failed"

        return False


    # =====================================================
    # LEARNED RETRY
    # =====================================================

    def learned_retry(self):

        if (
            self.learned_retry_count
            < self.max_learned_retries
        ):

            self.learned_retry_count += 1

            self.status = "retrying"

            return True

        self.status = "failed"

        return False


    # =====================================================
    # SHOW STATE
    # =====================================================

    def show_state(self):

        return {

            "goal": self.goal,

            "plan": self.plan,

            "current_step":
                self.current_step,

            "completed_steps":
                self.completed_steps,

            "results":
                self.results,

            "status":
                self.status,

            "retry_count":
                self.retry_count,

            "max_retries":
                self.max_retries,

            "learned_retry_count":
                self.learned_retry_count,

            "max_learned_retries":
                self.max_learned_retries,

            "error":
                self.error
        }