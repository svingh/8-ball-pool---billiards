#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdio.h>

#include "phylib.h"

phylib_object *phylib_new_still_ball(unsigned char number, phylib_coord *pos) {
    // Allocate memory for a new phylib_object
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));

    // Check if memory allocation was successful
    if (new_object == NULL) {
        return NULL;  // Return NULL if allocation failed
    }

    // Set the type of the object
    new_object->type = PHYLIB_STILL_BALL;

    // Initialize the still_ball data
    new_object->obj.still_ball.number = number;
    new_object->obj.still_ball.pos.x = pos->x;
    new_object->obj.still_ball.pos.y = pos->y;

    // Return the pointer to the new object
    return new_object;
}

phylib_object *phylib_new_rolling_ball(unsigned char number, phylib_coord *pos, phylib_coord *vel, phylib_coord *acc) {
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));
    if (new_object == NULL) {
        return NULL;
    }
    new_object->type = PHYLIB_ROLLING_BALL;
    new_object->obj.rolling_ball.number = number;
    new_object->obj.rolling_ball.pos = *pos;  
    new_object->obj.rolling_ball.vel = *vel;  
    new_object->obj.rolling_ball.acc = *acc;  
    return new_object;
}

phylib_object *phylib_new_hole(phylib_coord *pos) {
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));
    if (new_object == NULL) {
        return NULL;
    }
    new_object->type = PHYLIB_HOLE;
    new_object->obj.hole.pos = *pos;  
    return new_object;
}

phylib_object *phylib_new_hcushion(double y) {
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));
    if (new_object == NULL) {
        return NULL;
    }
    new_object->type = PHYLIB_HCUSHION;
    new_object->obj.hcushion.y = y;
    return new_object;
}

phylib_object *phylib_new_vcushion(double x) {
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));
    if (new_object == NULL) {
        return NULL;
    }
    new_object->type = PHYLIB_VCUSHION;
    new_object->obj.vcushion.x = x;
    return new_object;
}

phylib_table *phylib_new_table(void) {
    //Allocate memory for a new phylib_table
    phylib_table *new_table = (phylib_table *)malloc(sizeof(phylib_table));
    
    //Check if memory allocation was successful
    if (new_table == NULL) {
        return NULL;
    }

    //Initialize the time field
    new_table->time = 0.0;

    //Create and assign objects to the array
    new_table->object[0] = phylib_new_hcushion(0.0);  // Horizontal cushion at y = 0.0
    new_table->object[1] = phylib_new_hcushion(PHYLIB_TABLE_LENGTH);  // Horizontal cushion at y = table length
    new_table->object[2] = phylib_new_vcushion(0.0);  // Vertical cushion at x = 0.0
    new_table->object[3] = phylib_new_vcushion(PHYLIB_TABLE_WIDTH);  // Vertical cushion at x = table width

    // Adding holes
    new_table->object[4] = phylib_new_hole(&(phylib_coord){0.0, 0.0});  // Top-left corner
    new_table->object[5] = phylib_new_hole(&(phylib_coord){0.0, PHYLIB_TABLE_WIDTH});  // left-middle
    new_table->object[6] = phylib_new_hole(&(phylib_coord){0.0, PHYLIB_TABLE_LENGTH}); // left-bottom corner 
    new_table->object[7] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, 0.0});  // top-right corner
    new_table->object[8] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_WIDTH}); // right-middle
    new_table->object[9] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH}); // right-bottom

    // Set remaining pointers to NULL
    for (int i = 10; i < PHYLIB_MAX_OBJECTS; i++) {
        new_table->object[i] = NULL;
    }

    return new_table;
}


void phylib_copy_object(phylib_object **dest, phylib_object **src) {
    if (*src == NULL) {
        *dest = NULL;
    } else {
        *dest = (phylib_object *)malloc(sizeof(phylib_object));
        if (*dest != NULL) {
            memcpy(*dest, *src, sizeof(phylib_object));
        }
    }
}

phylib_table *phylib_copy_table(phylib_table *table) {
    if (table == NULL) {
        return NULL;
    }

    // Allocate memory for a new phylib_table
    phylib_table *new_table = (phylib_table *)malloc(sizeof(phylib_table));
    if (new_table == NULL) {
        return NULL;  // Return NULL if allocation failed
    }

    // Copy the time field from the source table
    new_table->time = table->time;

    // Iterate over each object in the source table
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        // copy each object
        phylib_copy_object(&(new_table->object[i]), &(table->object[i]));
    }

    // Return the new table with copied objects
    return new_table;
}

void phylib_add_object(phylib_table *table, phylib_object *object) {
    if (table == NULL || object == NULL) {
        return;
    }

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] == NULL) {
            table->object[i] = object;
            return;
        }
    }
}

void phylib_free_table(phylib_table *table) {
    if (table == NULL) {
        return;
    }

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] != NULL) {
            free(table->object[i]);
            table->object[i] = NULL;
        }
    }

    free(table);
}

phylib_coord phylib_sub(phylib_coord c1, phylib_coord c2) {
    phylib_coord result;
    result.x = c1.x - c2.x;
    result.y = c1.y - c2.y;
    return result;
}

double phylib_length(phylib_coord c) {
    // Length of the vector = sqrt(x^2 + y^2)
    return sqrt(c.x * c.x + c.y * c.y);
}

double phylib_dot_product(phylib_coord a, phylib_coord b) {
    // Dot product = a.x * b.x + a.y * b.y
    return a.x * b.x + a.y * b.y;
}

double phylib_distance(phylib_object *obj1, phylib_object *obj2) {
    // Check if obj1 is not a rolling ball
    if (obj1 == NULL || obj2 == NULL || obj1->type != PHYLIB_ROLLING_BALL) {
        return -1.0;
    }

    phylib_coord pos1 = obj1->obj.rolling_ball.pos;
    phylib_coord pos2;
    double distance;

    // Check the type of obj2 and calculate distance accordingly
    switch (obj2->type) {
        case PHYLIB_ROLLING_BALL: // Fall through to next case is intentional
        case PHYLIB_STILL_BALL:
            pos2 = obj2->obj.still_ball.pos;
            distance = phylib_length(phylib_sub(pos1, pos2)) - PHYLIB_BALL_DIAMETER;
            break;

        case PHYLIB_HOLE:
            pos2 = obj2->obj.hole.pos;
            distance = phylib_length(phylib_sub(pos1, pos2)) - PHYLIB_HOLE_RADIUS;
            break;

        case PHYLIB_HCUSHION:
            // horizontal cushion, only care about the y-coordinate difference
            distance = fabs(pos1.y - obj2->obj.hcushion.y) - PHYLIB_BALL_RADIUS;
            break;

        case PHYLIB_VCUSHION:
            // vertical cushion, only care about the x-coordinate difference
            distance = fabs(pos1.x - obj2->obj.vcushion.x) - PHYLIB_BALL_RADIUS;
            break;

        default:
            // If obj2 is not a recognized type, return -1.0
            return -1.0;
    }

    return distance;
}

void phylib_roll(phylib_object *new, phylib_object *old, double time) {
    // Ensure both objects are rolling balls
    if (new == NULL || old == NULL || 
        old->type != PHYLIB_ROLLING_BALL || new->type != PHYLIB_ROLLING_BALL) {
        return;  // Do nothing if either object is not a rolling ball
    }

    // Extract old position, velocity, and acceleration
    double p1_x = old->obj.rolling_ball.pos.x;
    double v1_x = old->obj.rolling_ball.vel.x;
    double a_x = old->obj.rolling_ball.acc.x;

    double p1_y = old->obj.rolling_ball.pos.y;
    double v1_y = old->obj.rolling_ball.vel.y;
    double a_y = old->obj.rolling_ball.acc.y;

    // Update new velocity
    double v_x = v1_x + a_x * time;
    double v_y = v1_y + a_y * time;

    // Check for change of sign in velocities to zero out velocities and accelerations
    if ((v1_x * v_x < 0) || (v1_y * v_y < 0)) {
        if (v1_x * v_x < 0) {
            v_x = 0;
            a_x = 0;
        }
        if (v1_y * v_y < 0) {
            v_y = 0;
            a_y = 0;
        }
    }

    // Update new position
    double p_x = p1_x + v1_x * time + 0.5 * a_x * time * time;
    double p_y = p1_y + v1_y * time + 0.5 * a_y * time * time;

    // Set new position and velocity
    new->obj.rolling_ball.pos.x = p_x;
    new->obj.rolling_ball.pos.y = p_y;

    new->obj.rolling_ball.vel.x = v_x;
    new->obj.rolling_ball.vel.y = v_y;

    // Set new acceleration (unchanged unless velocity changed sign)
    new->obj.rolling_ball.acc.x = a_x;
    new->obj.rolling_ball.acc.y = a_y;
}

unsigned char phylib_stopped(phylib_object *object) {
    if (object == NULL || object->type != PHYLIB_ROLLING_BALL) {
        return 0; // Return 0 if object is NULL or not a rolling ball
    }

    // Calculate the speed 
    double speed = phylib_length(object->obj.rolling_ball.vel);

    // Check ball has stopped
    if (speed < PHYLIB_VEL_EPSILON) {
        // Convert to STILL_BALL
        object->type = PHYLIB_STILL_BALL;
        
        // Transfer the number and position from the rolling ball to the still ball
        object->obj.still_ball.number = object->obj.rolling_ball.number;
        object->obj.still_ball.pos = object->obj.rolling_ball.pos;

        return 1; // Ball stopped converted to STILL_BALL
    }

    return 0; // Ball not stopped
}

void phylib_bounce(phylib_object **a, phylib_object **b) {
    if (a == NULL || *a == NULL || (*a)->type != PHYLIB_ROLLING_BALL) {
        return; // a is not a rolling ball or is NULL, so do nothing
    }

    if((*b)->type == PHYLIB_STILL_BALL){
    }

    switch ((*b)->type) {
        case PHYLIB_HCUSHION:
            (*a)->obj.rolling_ball.vel.y *= -1;
            (*a)->obj.rolling_ball.acc.y *= -1;
            break;

        case PHYLIB_VCUSHION:
            (*a)->obj.rolling_ball.vel.x *= -1;
            (*a)->obj.rolling_ball.acc.x *= -1;
            break;

        case PHYLIB_HOLE:
            free(*a);
            *a = NULL;
            break;

        case PHYLIB_STILL_BALL:
            (*b)->type = PHYLIB_ROLLING_BALL;
            (*b)->obj.rolling_ball.pos = (*b)->obj.still_ball.pos;
            (*b)->obj.rolling_ball.number = (*b)->obj.still_ball.number;
            (*b)->obj.rolling_ball.vel.x = 0;
            (*b)->obj.rolling_ball.vel.y = 0;
            (*b)->obj.rolling_ball.acc.x = 0;
            (*b)->obj.rolling_ball.acc.y = 0;
            // No break here, the logic should continue to PHYLIB_ROLLING_BALL

        case PHYLIB_ROLLING_BALL:
            {
                // Compute the position of a with respect to b
                phylib_coord r_ab = phylib_sub((*a)->obj.rolling_ball.pos, (*b)->obj.rolling_ball.pos);

                // Compute the relative velocity of a with respect to b
                phylib_coord v_rel = phylib_sub((*a)->obj.rolling_ball.vel, (*b)->obj.rolling_ball.vel);

                // Calculate the unit normal vector n.
                double length_r_ab = phylib_length(r_ab);
                phylib_coord n = { r_ab.x / length_r_ab, r_ab.y / length_r_ab };

                // Calculate the relative velocity of a in the direction of the normal vector, v_rel_n.
                double v_rel_n = phylib_dot_product(v_rel, n);

                // Update the x and y velocities of ball a 
                (*a)->obj.rolling_ball.vel.x -= v_rel_n * n.x;
                (*a)->obj.rolling_ball.vel.y -= v_rel_n * n.y;

                // Update the x and y velocities of ball b.
                (*b)->obj.rolling_ball.vel.x += v_rel_n * n.x;
                (*b)->obj.rolling_ball.vel.y += v_rel_n * n.y;

                // Compute the speed of a and b as the lengths of their velocities.
                double speed_a = phylib_length((*a)->obj.rolling_ball.vel);
                double speed_b = phylib_length((*b)->obj.rolling_ball.vel);

                // If speed > EPSILON, acceleration ball negative
                // velocity divided by the speed multiplied by DRAG.
                if (speed_a > PHYLIB_VEL_EPSILON) {
                    (*a)->obj.rolling_ball.acc.x = -((*a)->obj.rolling_ball.vel.x * PHYLIB_DRAG) / speed_a;
                    (*a)->obj.rolling_ball.acc.y = -((*a)->obj.rolling_ball.vel.y * PHYLIB_DRAG) / speed_a;
                } else {
                    (*a)->obj.rolling_ball.vel.x = 0;
                    (*a)->obj.rolling_ball.vel.y = 0;
                    (*a)->obj.rolling_ball.acc.x = 0;
                    (*a)->obj.rolling_ball.acc.y = 0;
                }

                if (speed_b > PHYLIB_VEL_EPSILON) {
                    (*b)->obj.rolling_ball.acc.x = -((*b)->obj.rolling_ball.vel.x * PHYLIB_DRAG) / speed_b;
                    (*b)->obj.rolling_ball.acc.y = -((*b)->obj.rolling_ball.vel.y * PHYLIB_DRAG) / speed_b;
                } else {
                    (*b)->obj.rolling_ball.vel.x = 0;
                    (*b)->obj.rolling_ball.vel.y = 0;
                    (*b)->obj.rolling_ball.acc.x = 0;
                    (*b)->obj.rolling_ball.acc.y = 0;
                }
                break;
            }

        default:
            // Any other object type
            break;
    }
}

unsigned char phylib_rolling(phylib_table *t) {
    if (t == NULL) {
        return 0; // If NULL pointer, return 0
    }

    unsigned char count = 0;
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (t->object[i] != NULL && t->object[i]->type == PHYLIB_ROLLING_BALL) {
            count++;
        }
    }

    return count;
}

phylib_table *phylib_segment(phylib_table *table)
{
    // Create a copy of the table 
    phylib_table *copy = phylib_copy_table(table);
    if (copy == NULL) {
        return NULL; // Failed to create a copy
    }

    // If no balls are rolling, free the result table and return NULL
    if (phylib_rolling(table) == 0) {
        phylib_free_table(copy);
        return NULL;
    }

    // Loop through each time step within the simulation rate

    // double time = PHYLIB_SIM_RATE;
    for (double time = table->time + PHYLIB_SIM_RATE; time <= PHYLIB_MAX_TIME; time += PHYLIB_SIM_RATE) {
        copy->time = time; // Update time for the result table
        int collision_occurred = 0; // Flag for collision occurrence

        // Loop through each object in the table
        for (int i = 0; i < PHYLIB_MAX_OBJECTS && !collision_occurred; i++) {
            if (copy->object[i] != NULL && copy->object[i]->type == PHYLIB_ROLLING_BALL) {
                phylib_roll(copy->object[i], copy->object[i], PHYLIB_SIM_RATE);

                if (phylib_stopped(copy->object[i])) {
                    //copy->time = table->time + time
                    return copy;
                }
            }
        }
        for (int i = 0; i < PHYLIB_MAX_OBJECTS && !collision_occurred; i++) {
            if (copy->object[i] != NULL && copy->object[i]->type == PHYLIB_ROLLING_BALL) {
                // Check for collisions with other objects
                for (int j = 0; j < PHYLIB_MAX_OBJECTS; j++) {
                    double distance = phylib_distance(copy->object[i], copy->object[j]);
                    if (i != j && copy->object[j] != NULL && distance < 0.0) {
                        phylib_bounce(&copy->object[i], &copy->object[j]);
                        collision_occurred = 1; // Mark collision
                        break; // Break inner loop to handle one event at a time
                    }
                }
            }
        }

        // If a collision occurred, return the updated table immediately
        if (collision_occurred) {
            return copy;
        }
    }
    return copy;
}

//new function
char *phylib_object_string( phylib_object *object )
{
    static char string[80];
    if (object==NULL)
    {
        snprintf( string, 80, "NULL;" );
        return string;
    }
    switch (object->type)
    {
        case PHYLIB_STILL_BALL:
            snprintf( string, 80,
                "STILL_BALL (%d,%6.1lf,%6.1lf)",
                object->obj.still_ball.number,
                object->obj.still_ball.pos.x,
                object->obj.still_ball.pos.y );
            break;
        case PHYLIB_ROLLING_BALL:
            snprintf( string, 80,
                "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
                object->obj.rolling_ball.number,
                object->obj.rolling_ball.pos.x,
                object->obj.rolling_ball.pos.y,
                object->obj.rolling_ball.vel.x,
                object->obj.rolling_ball.vel.y,
                object->obj.rolling_ball.acc.x,
                object->obj.rolling_ball.acc.y );
            break;
        case PHYLIB_HOLE:
            snprintf( string, 80,
                "HOLE (%6.1lf,%6.1lf)",
                object->obj.hole.pos.x,
                object->obj.hole.pos.y );
            break;
        case PHYLIB_HCUSHION:
            snprintf( string, 80,
                "HCUSHION (%6.1lf)",
                object->obj.hcushion.y );
            break;
        case PHYLIB_VCUSHION:
            snprintf( string, 80,
                "VCUSHION (%6.1lf)",
                object->obj.vcushion.x );
            break;
    }
    return string;
}

