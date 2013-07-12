/**
 * @file Timers.java
 * @author Marcus Edel
 *
 * Class to provide timers.
 */

import java.util.HashMap;

/**
 * The timer class provides a way for methods to be timed. The three methods 
 * contained in this class allow a named timer to be started and stopped, and
 * its value to be obtained.
 */
public class Timers {
	private HashMap<String, Long> timers = new HashMap<String, Long>();

	/**
   * Start the given timer.  If a timer is started, then stopped, then
   * re-started, then re-stopped, the final value of the timer is the length of
   * both runs.
   *
   * @note Undefined behavior will occur if a timer is started twice.
   *
   * @param timerNname - Name of timer to be started.
   */
	public void StartTimer(final String timerNname) {
		timers.put(timerNname, System.nanoTime());
	}

	/**
   * Stop the given timer.
   *
   * @note Undefined behavior will occur if a timer is started twice.
   *
   * @param timerName - Name of timer to be stopped.
   */
	public void StopTimer(final String timerName) {
		Long time = timers.get(timerName);
		if (time != null) {
			timers.put(timerName, (System.nanoTime() - time));
		}
	}

	/**
   * Get the value of the given timer.
   *
   * @param timerName - Name of timer to return value of.
   */
	public Long GetTimer(final String timerName) throws Exception {
		Long time = timers.get(timerName);
		if (time == null) {
			throw new Exception("There exists no timer with this name.");
		}

		return time;
	}

	/**
   * Prints the specified timer.
   *
   * @param timerName The name of the timer in question.
   */
	public void PrintTimer(final String timerName) throws Exception {
		Long time = timers.get(timerName);
		if (time == null) {
			throw new Exception("There exists no timer with this name.");
		}

		System.out.printf("[INFO ]   %s: %fs\n", timerName, (time / 1e9));
	}
}